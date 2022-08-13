# TODO: Заменить все русские строки на английские.
import socket
import json
import os
import pathlib


class ConnectionIsNotEstablishedError(Exception):
    """ Ошибка попытки отправить пакет на сервер,
    подключение с котороым не было инициализировано
    """


class PacketFormatError(Exception):
    """ Ошибка формата пакета. Чаще всего используется,
    когда обязательное поле пакета не заполнено, например,
    'command'
    """


class SessionDirectoryError(Exception):
    """ Ошибка в директории админской сессии. Чаще всего
    вызывается в случае, когда файл сессии имеет неверное имя
    (например, кол-во чисел в названии отличается) или в
    директории имеется несколько файлов сессии, что недопустимо.
    """


class Session:
    """ Менеджер сессий. Формирует пакеты
     на авторизацию аккаунта администратора,
     реагирует на ошибки сессий и получает их
     из директории /var/tmp/crcs_session/ """
    SESSION_DIR = pathlib.Path("/var/tmp/crcs_session/")

    if not SESSION_DIR.exists():
        SESSION_DIR.mkdir()

    def __init__(self):

        files_in_session_directory = os.listdir(Session.SESSION_DIR)

        if len(files_in_session_directory) > 1:
            raise SessionDirectoryError("В директории админских сессий было обнаружено более двух файлов.")
        elif len(files_in_session_directory) == 0:
            raise SessionDirectoryError("Сессия отсутствует.")
        else:
            self._sessionuid = files_in_session_directory[0]

    def remove(self):
        """ Удаляет файл сессии """
        Session.SESSION_DIR.joinpath(self._sessionuid).unlink()


class CommandPacket:
    """ Класс пакета команды, которую должен выполнить клиент.
    Используется в методах отправки данных на сервер """
    def __init__(self):
        self.__command = None     # Команда, которую должен исполнить клиент
        self.__args = []          # Аргументы команды
        self.__sessionuid = None  # Идентификатор сессии текущего администратора
        self.__pooluid = None     # Идентификатор пула хостов

    def set_command(self, command: str) -> None:
        self.__command = command

    def set_arg(self, argument: str) -> None:
        self.__args.append(argument)

    def set_session(self, session: Session) -> None:
        self.__sessionuid = session

    def set_pool(self, pool: int) -> None:
        self.__pooluid = pool

    def format_to_packet_bytes(self) -> bytes:
        """ Формирует пакет для отправки по сети,
        основанный на json, используя атрибуты текущего
        экземпляра пакета """
        packet = {
            "command": None,
            "args": [],
            "sessionuid": None,
            "pooluid": None
        }

        if self.__command:
            packet["command"] = self.__command
        else:
            raise PacketFormatError("Required package parameter \"command\" was not filled.")

        for argument in self.__args:
            packet["args"].append(argument)

        if self.__sessionuid:
            packet["sessionuid"] = self.__sessionuid
        else:
            raise PacketFormatError("Required package parameter \"sessionuid\" was not filled.")

        if self.__pooluid:
            packet["pooluid"] = self.__pooluid
        else:
            raise PacketFormatError("Required package parameter \"pooluid\" was not filled.")

        return json.dumps(packet).encode("utf8")


class ServerConnection:
    """ Класс подключения к серверу """
    MID_CONN_SERVER_HOST = "127.0.0.1"
    MID_CONN_SERVER_PORT = 708

    def __init__(self):
        self.__socket = None         # Атрибут клиентского сокета. Создается при инициализации подключения
        self.__is_connected = False  # Флаг подключения. Нужен для выполнения логических
                                     # операций, отличных от отправки пакетов на сервер

    def init(self, polling: bool = False):
        """ Инициализирует подключение к серверу, после чего
        можно использовать методы класса для отправки команд """
        self.__is_connected = True

        self.__socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP
        )

        self.__socket.connect((ServerConnection.MID_CONN_SERVER_HOST, ServerConnection.MID_CONN_SERVER_PORT))

    def close(self):
        """ Разрывает подключение """
        if not self.__is_connected:
            raise ConnectionIsNotEstablishedError("Trying to use the network method without connecting to the server")

        self.__is_connected = False
        self.__socket.close()

    def send_packet(self, packet: CommandPacket) -> str:
        """ Отправляет пакет с командами.

        :param packet - Экземпляр класса CommandPacket,
        предварительно сформированный при помощи его методов.
        """
        if not self.__is_connected:
            raise ConnectionIsNotEstablishedError("Trying to use the network method without connecting to the server")

        self.__socket.send(packet.format_to_packet_bytes())

        responce = self.__socket.recv(2048)

        self.close()

        # TODO: Нужно додумать способ подключения к центральному серверу: разрывать ли подключение после каждой
        #   введенной команды и устанавливать новое, либо оставаться на текущем; а также определиться с типом,
        #   который возвращает функция: это будет строка с ответом, либо какой-то экземпляр класса.

        return responce

    def auth(self):
        """ Отправляет пакет аутентификации. Сервер возвращает
        код ответа
        """
        pass


if __name__ == "__main__":
    # Блок для реализации Cli интерфейса на основе созданных классов
    session = Session()
    print(session.remove())
