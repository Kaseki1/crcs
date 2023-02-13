#!/usr/bin/python3
import clientlib
import ctypes
from termcolor import colored
import pathlib
import socket
import abc
import json
import sys
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
    FILE_ID_DIR = None

    if sys.platform == "linux" or sys.platform == "linux2":
        FILE_ID_DIR = pathlib.Path("/var/tmp/crcs_host_id/")

        if not FILE_ID_DIR.exists():
            FILE_ID_DIR.mkdir()

    elif sys.platform == "win32":
        FILE_ID_DIR = os.path.dirname(os.path.abspath(__file__))

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
        default_data_template = {
            "saved_hostname": socket.gethostname()
        }

        with open(HostUIDFile.FILE_ID_DIR.joinpath(host_id), "w") as fp:
            json.dump(default_data_template, fp)

    @property
    def saved_hostname(self):
        with open(HostUIDFile.FILE_ID_DIR.joinpath(self.__host_id), "r") as fp:
            return json.load(fp)["saved_hostname"]

    @saved_hostname.setter
    def saved_hostname(self, value):
        # TODO: сделать так, чтобы этот код работал только с одним дескриптором, а не с двумя
        with open(HostUIDFile.FILE_ID_DIR.joinpath(self.__host_id), "r") as fp:
            data = json.load(fp)
            data["saved_hostname"] = value

        with open(HostUIDFile.FILE_ID_DIR.joinpath(self.__host_id), "w") as fp:
            json.dump(data, fp)


class ServerConnection:
    """ Класс подключения к серверу """
    MID_CONN_SERVER_HOST = "18.178.86.139"
    MID_CONN_SERVER_PORT = 9091
    RECV_BUFF_SIZE = 16384
    TERMINATOR = b"\x04"

    def __init__(self):
        self.__socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP
        )

        self.__socket.connect((ServerConnection.MID_CONN_SERVER_HOST, ServerConnection.MID_CONN_SERVER_PORT))

    def init_pool(self, pool_uid: int, hostname: str = socket.gethostname()) -> bool:
        """ Инициализирует клиента в пуле """
        # x------------------------------------x
        # |          !!! WARNING !!!           |
        # | В этой функции стоит блокировка на |
        # | вступление в несколько пулов.      |
        # x------------------------------------x
        try:
            HostUIDFile()
            self.__socket.close()
            raise PoolAlreadyInit("Pool already init.")
        except HostUIDDirectoryError:
            init_packet = InitPacket(pool_uid, hostname)
            self.__socket.send(init_packet.convert_to_packet_bytes() + ServerConnection.TERMINATOR)
            result = ServerResponse(self.__socket.recv(ServerConnection.RECV_BUFF_SIZE))
            HostUIDFile.save_host_id(result.DATA)
            self.__socket.close()

            return result.CODE

    def start_session(self):
        self.__socket.send(ReadyPacket().convert_to_packet_bytes() + ServerConnection.TERMINATOR)

    def logout(self):
        """ Инициирует выход из пула """
        packet = LeavePoolPacket()
        self.__socket.send(packet.convert_to_packet_bytes() + ServerConnection.TERMINATOR)
        result = ServerResponse(self.__socket.recv(ServerConnection.RECV_BUFF_SIZE))

        if result.CODE == "success":
            host_file = HostUIDFile()
            host_file.remove()

    def handle_commands(self, handler) -> None:
        """ После установленного постоянного подключения принимает
         команды от администратора и возвращает результат функции-обработчика.
         """
        while True:
            data = self.__socket.recv(ServerConnection.RECV_BUFF_SIZE)
            command = json.loads(data)["command"]
            print(f"[?] Получен запрос: {command}")
            handled_command = handler(command)
            self.__socket.send(handled_command.convert_to_packet_bytes() + ServerConnection.TERMINATOR)
            break

        return command


class BasePacket(abc.ABC):
    """ Базовый класс всех пакетов """

    def __init__(self):
        self._operation_type: str  # Указывает формат пакета

    @abc.abstractmethod
    def convert_to_packet_bytes(self) -> bytes:
        """ Конвертирует объект пакета в поток байт """
        pass


class InitPacket(BasePacket):
    def __init__(self, pool_id: int, hostname: str = socket.gethostname()):
        super().__init__()
        self._operation_type: str = "init"
        self.hostname: str = hostname
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


class LeavePoolPacket(BasePacket):
    """ Реализация пакета выхода из пула. """
    def __init__(self, host_id: HostUIDFile = None):
        super().__init__()

        self._operation_type = "del"
        self.host_id: HostUIDFile = host_id

        if not host_id:
            self.host_id = HostUIDFile()

    def convert_to_packet_bytes(self) -> bytes:
        packet_json_format = {
            "op_type": self._operation_type,
            "host_id": None
        }

        if self.host_id:
            packet_json_format["host_id"] = self.host_id.get_host_id()
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
            "op_type": self._operation_type,
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
    # --------------------------------------------------------------------
    # [[ УТИЛИТА FS ]]
    if command == "fs pwd":
        return ResponsePacket(clientlib.get_current_path())

    elif command.startswith("fs cd "):
        try:
            return ResponsePacket(clientlib.change_path(command[6::]))
        except FileNotFoundError:
            return ResponsePacket(is_success=False)

    elif command.startswith("fs ls"):
        parts = command.split(" ")

        if len(parts) > 2:
            return ResponsePacket(clientlib.get_file_list(command[6::]))
        else:
            return ResponsePacket(clientlib.get_file_list("*"))

    elif command.startswith("fs cat "):
        try:
            return ResponsePacket(clientlib.get_file_content(command[7::]))
        except FileNotFoundError:
            return ResponsePacket(is_success=False)

    elif command.startswith("fs rm "):
        try:
            return ResponsePacket(clientlib.remove_file(command[6::]))
        except FileNotFoundError:
            return ResponsePacket(is_success=False)

    elif command.startswith("sh "):
        return ResponsePacket(clientlib.process_shell_command(command[3::]))
    # --------------------------------------------------------------------

    # Если команда не была найдена/реализована, то отправляется код ошибки.
    return ResponsePacket(is_success=False, comment="Неизвестная команда.")


if __name__ == "__main__":
    if sys.platform == "win32":
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    try:
        if sys.argv[1] == "connect":
            connection = ServerConnection()
            result = connection.init_pool(int(sys.argv[2]))

            if result:
                print(f"[{colored('+', 'green')}] Вы успешно вступили в пул.\n")
            else:
                print(f"[{colored('-', 'red')}] Ошибка вступления в пул.\n")

        elif sys.argv[1] == "logout":
            connection = ServerConnection()
            connection.logout()
            print(f"[{colored('+', 'green')}] Пул успешно покинут.\n")

        elif sys.argv[1] == "start":
            connection = ServerConnection()
            connection.start_session()

            print(f"[{colored('+', 'green')}] Сессия обработки команд успешно запущена ...\n")

            while True:
                connection.handle_commands(main_handler)

        elif sys.argv[1] == "--help":
            print(f"""[{colored('?', 'yellow')}] Список аргументов админской панели.
Последнее обновление: 12.09.2022\n
* connect [pool_id] - Подключается к пулу с номером, указанным в pool_id.
* start - Начинает сессию обработки админских команд.
* logout - Выход из пула.
""")

        else:
            print(f"[{colored('-', 'red')}] Аргумент команды был введен некорректно. "
                  f"Для справки воспользуйтесь опцией --help\n")
    except IndexError:
        print(f"[{colored('-', 'red')}] Аргумент команды был введен некорректно. "
              f"Для справки воспользуйтесь опцией --help\n")
    except PoolAlreadyInit:
        print(f"[{colored('-', 'red')}] Вы уже вступили в пул. Файл host_id был найден в директории.\n")
    except HostUIDDirectoryError:
        print(f"[{colored('-', 'red')}] Вы не вступили ни в один пул.\n")
    except ConnectionRefusedError:
        print(f"[{colored('-', 'red')}] Подключение было разорвано центральным сервером.\n")
