from clientlib import filesystem
from termcolor import colored
import getpass
import pathlib
import socket
import abc
import json
import os


class PoolAlreadyInit(Exception):
    """ Блокировка, которая сообщает о том,
     что клиент на данный момент уже присоединен к пулу
     и не может одновременно вступить в другой.
    """


class PacketFormatError(Exception):
    """ Ошибка формата пакета. Чаще всего используется,
    когда обязательное поле пакета не заполнено, например,
    'command'
    """


class HostUIDDirectoryError(Exception):
    """ Ошибка в директории клиентского идентификатора. Чаще всего
     вызывается в случае, когда файл-идентификатор имеет неверное имя
     (например, кол-во чисел в названии отличается) или в
     директории имеется несколько файлов-идентификаторов, что недопустимо.
    """


class HostUIDFile:
    """ Менеджер файла host_id клиента,
     который находится в /usr/tmp/host_id/
    """
    FILE_ID_DIR = pathlib.Path("/var/tmp/crcs_host_id/")

    if not FILE_ID_DIR.exists():
        FILE_ID_DIR.mkdir()

    def __init__(self):
        files_in_host_id_directory = os.listdir(HostUIDFile.FILE_ID_DIR)

        if len(files_in_host_id_directory) > 1:
            raise HostUIDDirectoryError("В директории клиентских идентификаторов было обнаружено более одного файла.")

            # При обнаружении нескольких файлов сессий в директории -
            # удаляет их из директории.
            for file in files_in_host_id_directory:
                HostUIDFile.FILE_ID_DIR.joinpath(file).unlink()

        elif len(files_in_host_id_directory) == 0:
            raise HostUIDDirectoryError("Отсутствует клиентский идентификатор.")
        else:
            self.__host_id = files_in_host_id_directory[0]

    def get_host_id(self):
        return self.__host_id

    def remove(self):
        """ Удаляет файл сессии """
        HostUIDFile.FILE_ID_DIR.joinpath(str(self.__host_id)).unlink()

    @staticmethod
    def save_host_id(host_id: str):
        """ Сохраняет файл сессии в директорию админской сессии """
        with open(HostUIDFile.FILE_ID_DIR.joinpath(host_id), "w") as fp:
            pass


class ServerConnection:
    """ Класс подключения к серверу """
    MID_CONN_SERVER_HOST = "192.168.1.71"
    MID_CONN_SERVER_PORT = 9091
    RECV_BUFF_SIZE = 2048

    def __init__(self):
        self.__socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP
        )

        self.__socket.connect((ServerConnection.MID_CONN_SERVER_HOST, ServerConnection.MID_CONN_SERVER_PORT))

    def init_pool(self, pool_uid: int) -> bool:
        """ Инициализирует клиента в пуле """
        # x------------------------------------x
        # |          !!! WARNING !!!           |
        # | В этой функции стоит блокировка на |
        # | вступление в несколько пулов.      |
        # x------------------------------------x
        try:
            HostUIDFile()
            raise PoolAlreadyInit("Pool already init.")
        except HostUIDDirectoryError:
            init_packet = InitPacket(pool_uid)
            self.__socket.send(init_packet.convert_to_packet_bytes())
            result = ServerResponse(self.__socket.recv(ServerConnection.RECV_BUFF_SIZE))
            HostUIDFile.save_host_id(result.DATA)

            return result.CODE

    def start_session(self) -> None:
        """ Отправляет пакет подключения к пулу на сервер.
        Нужен для того, чтобы на сервере обновлялся IP адрес в БД,
        на который нужно пересылать команды. Также, сообщает серверу о
        готовности принимать команды, в следствие чего хост впадает в
        бесконечное ожидание.
        """
        packet = ReadyPacket()
        self.__socket.send(packet.convert_to_packet_bytes())

    def handle_command(self, handler) -> None:
        """ После установленного постоянного подключения принимает
         команды от администратора и возвращает результат функции-обработчика.
         """
        data = self.__socket.recv(ServerConnection.RECV_BUFF_SIZE)
        print(json.loads(data))
        command = json.loads(data)["command"]

        self.__socket.send(handler(command).convert_to_packet_bytes())


class BasePacket(abc.ABC):
    """ Базовый класс всех пакетов """

    def __init__(self):
        self._operation_type: str  # Указывает формат пакета

    @abc.abstractmethod
    def convert_to_packet_bytes(self) -> bytes:
        """ Конвертирует объект пакета в поток байт """
        pass


class InitPacket(BasePacket):
    def __init__(self, pool_id: int):
        super().__init__()
        self._operation_type: str = "init"
        self.hostname: str = socket.gethostname()
        self.pool_id: int = pool_id

    def convert_to_packet_bytes(self) -> bytes:
        packet_json_format = {
            "op_type": self._operation_type,
            "hostname": None,
            "pool_id": None
        }

        if self.hostname:
            packet_json_format["hostname"] = self.hostname
        else:
            raise PacketFormatError("Required package parameter \"hostname\" was not filled.")

        if self.pool_id:
            packet_json_format["pool_id"] = self.pool_id
        else:
            raise PacketFormatError("Required package parameter \"pool_id\" was not filled.")

        return json.dumps(packet_json_format).encode("utf8")


class ReadyPacket(BasePacket):
    """ Реализация пакета подключения к серверу. Отправляется каждый
     раз, когда клиент подключается к серверу.
    """
    def __init__(self, host_id: HostUIDFile = None):
        super().__init__()

        self._operation_type = "ready"
        self.host_id: HostUIDFile = host_id

        if not host_id:
            self.host_id = HostUIDFile()

    def convert_to_packet_bytes(self) -> bytes:
        packet_json_format = {
            "op_type": "ready",
            "host_id": None
        }

        if self.host_id:
            packet_json_format["host_id"] = self.host_id.get_host_id()
        else:
            raise PacketFormatError("Required package parameter \"pool_id\" was not filled.")

        return json.dumps(packet_json_format).encode("utf8")


class ResponsePacket(BasePacket):
    """ Класс для сборки ответа клиента
    на запрос администратора.
    """
    def __init__(self, data=None, is_success: bool = True, comment: str = ""):
        super().__init__()
        self.IS_SUCCESS = is_success
        self.COMMENT = comment
        self.DATA = data

    def convert_to_packet_bytes(self) -> bytes:
        if self.IS_SUCCESS:
            code = "success"
        else:
            code = "error"

        packet_json_format = {
            "code": code,
            "comment": self.COMMENT,
            "data": self.DATA
        }

        # TODO: Сделать проверку на наличие данных полей в экземпляре.

        return json.dumps(packet_json_format).encode("utf8")


class ServerResponse:
    """ ООП реализация ответа сервера """
    def __init__(self, response: bytes):
        data = json.loads(response)

        self.CODE = data["code"]
        self.COMMENT = data["comment"]
        self.DATA = data["data"]


def main_handler(command: str):
    """ Обработчик команд администратора """
    # [[ УТИЛИТА FS ]]
    if command == "fs pwd":
        return ResponsePacket(filesystem.get_current_path(), comment="Путь изменен: ")

    elif command.startswith("fs cd "):
        try:
            return ResponsePacket(filesystem.change_path(command.split(" ")[2]))
        except FileNotFoundError:
            return ResponsePacket(is_success=False, comment="No such file ro directory.")

    elif command == "fs ls":
        return ResponsePacket(filesystem.get_file_list())

    elif command.startswith("fs cat "):
        return ResponsePacket(filesystem.get_file_content(command.split(" ")[2]))
    # ---------------------

    # Если команда не была найдена/реализована, то отправляется код ошибки.
    return ResponsePacket(is_success=False, comment="Неизвестная команда.")


if __name__ == "__main__":
    # TODO: Реализовать клиентский GUI и демонизацию процесса.
    while True:
        command = input("[main] ").strip()
        connection = ServerConnection()

        if command == "logout":
            try:
                host_file = HostUIDFile()
                host_file.remove()
                print(f"[{colored('+', 'green')}] Пул успешно покинут.")
            except HostUIDDirectoryError:
                print(f"[{colored('-', 'red')}] Вы не вступили ни в один пул.")

        elif command.startswith("connect "):
            try:
                pool_id = command.split(" ")[1]
                result = connection.init_pool(int(pool_id))

                if result:
                    print(f"[{colored('+', 'green')}] Вы успешно вступили в пул.")
                else:
                    print(f"[{colored('-', 'red')}] Ошибка вступления в пул.")  # TODO: Сделать комментарий от сервера.
            except PoolAlreadyInit:
                print(f"[{colored('-', 'red')}] Вы уже вступили в пул. Файл host_id был найден в директории.")

        elif command == "start":
            connection = ServerConnection()
            connection.start_session()

            while True:
                connection.handle_command(main_handler)
