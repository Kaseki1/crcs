from termcolor import colored
import getpass
import socket
import json
import os
import pathlib
import abc


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
     из директории /var/tmp/crcs_session/
     """
    SESSION_DIR = pathlib.Path("/var/tmp/crcs_session/")

    if not SESSION_DIR.exists():
        SESSION_DIR.mkdir()

    def __init__(self):
        files_in_session_directory = os.listdir(Session.SESSION_DIR)

        if len(files_in_session_directory) > 1:
            raise SessionDirectoryError("В директории админских сессий было обнаружено более двух файлов.")

            # При обнаружении нескольких файлов сессий в директории -
            # удаляет их из директории.
            for file in files_in_session_directory:
                Session.SESSION_DIR.joinpath(file).unlink()

        elif len(files_in_session_directory) == 0:
            raise SessionDirectoryError("Сессия отсутствует.")
        else:
            self.__sessionuid = files_in_session_directory[0]

    def get_session_uid(self):
        return self.__sessionuid

    def remove(self):
        """ Удаляет файл сессии """
        Session.SESSION_DIR.joinpath(str(self.__sessionuid)).unlink()


class BasePacket(abc.ABC):
    """ Базовый класс всех пакетов """

    def __init__(self):
        self._operation_type: str  # Указывает формат пакета

    @abc.abstractmethod
    def convert_to_packet_bytes(self) -> bytes:
        """ Конвертирует объект пакета в поток байт """
        pass


class CommandPacket(BasePacket):
    """ Класс пакета команды, которую должен выполнить клиент.
    Используется в методах отправки данных на сервер.
    """

    def __init__(self, command: str = None, pool: int = None, session: Session = None):
        super().__init__()

        if not session:
            session = Session()

        self._operation_type = "command"
        self.__command: str = command      # Команда, которую должен исполнить клиент
        self.__session: Session = session  # Идентификатор сессии текущего администратора
        self.__pool: int = pool            # Идентификатор пула хостов

    def set_command(self, command: str) -> None:
        self.__command = command

    def set_session(self, session: Session) -> None:
        self.__session = session

    def set_pool(self, pool: int) -> None:
        self.__pool = pool

    def convert_to_packet_bytes(self) -> bytes:
        """ Формирует пакет для отправки по сети,
        основанный на json, используя атрибуты текущего
        экземпляра пакета """
        packet = {
            "op_type": self._operation_type,
            "command": None,
            "sessionuid": None,
            "pooluid": None
        }

        # Далее идет проверка введение полей пакета.
        if self.__command:
            packet["command"] = self.__command
        else:
            raise PacketFormatError("Required package parameter \"command\" was not filled.")

        if self.__session:
            packet["sessionuid"] = self.__session.get_session_uid()
        else:
            raise PacketFormatError("Required package parameter \"sessionuid\" was not filled.")

        if self.__pool:
            packet["pooluid"] = self.__pool
        else:
            raise PacketFormatError("Required package parameter \"pooluid\" was not filled.")

        return json.dumps(packet).encode("utf8")


class AuthPacket(BasePacket):
    """ Реализация формата пакета для аутентификации
    личного кабинета администратора сети.
    """

    def __init__(self, login: str = None, password: str = None):
        super().__init__()

        self._operation_type = "auth"
        self._login: str = login  # Логин личного кабинета администратора
        self._password: str = password  # Пароль личного кабинета администратора

    def login(self, login: str, password: str) -> None:
        self._login = login
        self._password = password

    def convert_to_packet_bytes(self) -> bytes:
        packet_json_format = {
            "op_type": self._operation_type,
            "login": None,
            "password": None
        }

        if self._login:
            packet_json_format["login"] = self._login
        else:
            raise PacketFormatError("Required package parameter \"login\" was not filled.")

        if self._password:
            packet_json_format["password"] = self._password
        else:
            raise PacketFormatError("Required package parameter \"password\" was not filled.")

        return json.dumps(packet_json_format).encode("utf8")


class RegistrationPacket(BasePacket):
    """ Реализация формата пакета для регистрации
    личного кабинета администратора сети.
    """

    def __init__(self, login: str = None, password: str = None, email: str = None):
        super().__init__()

        self._operation_type = "reg"
        self._login: str = login  # Логин личного кабинета администратора
        self._password: str = password  # Пароль личного кабинета администратора
        self._email: str = email  # Почта администратора

    def login(self, login: str, password: str) -> None:
        self._login = login
        self._password = password

    def set_email(self, email: str) -> None:
        self._email = email

    def convert_to_packet_bytes(self) -> bytes:
        packet_json_format = {
            "op_type": self._operation_type,
            "login": None,
            "password": None,
            "email": None
        }

        if self._login:
            packet_json_format["login"] = self._login
        else:
            raise PacketFormatError("Required package parameter \"login\" was not filled.")

        if self._password:
            packet_json_format["password"] = self._password
        else:
            raise PacketFormatError("Required package parameter \"password\" was not filled.")

        if self._email:
            packet_json_format["email"] = self._email
        else:
            raise PacketFormatError("Required package parameter \"email\" was not filled.")

        return json.dumps(packet_json_format).encode("utf8")


class ServerPacket(BasePacket):
    """ Реализует формат пакета,
     адресованного центральному серверу.
    """

    def __init__(self, request: str = None, session: Session = None):
        super().__init__()

        if not session:
            session = Session()

        self._operation_type = "server"
        self.__request: str = request
        self.__session: Session = session

    def set_session(self, session: Session):
        self.__session = session

    def set_request(self, request: str):
        self.__request = request

    def convert_to_packet_bytes(self) -> bytes:
        packet_json_format = {
            "op_type": self._operation_type,
            "request": None,
            "sessionuid": None
        }

        if self.__request:
            packet_json_format["request"] = self.__request
        else:
            raise PacketFormatError("Required package parameter \"request\" was not filled.")

        if self.__session:
            packet_json_format["sessionuid"] = self.__session.get_session_uid()
        else:
            raise PacketFormatError("Required package parameter \"sessionuid\" was not filled.")

        return json.dumps(packet_json_format).encode("utf8")


class ServerResponsePacket:
    """ ООП представление пакета ответа сервера.
    Возвращается в классе ServerConnection.
    """
    def __init__(self, response: bytes):
        data = json.loads(response)

        self.CODE = data["code"]
        self.COMMENT = data["comment"]
        self.DATA = data["data"]


class ServerConnection:
    """ Класс подключения к серверу """
    MID_CONN_SERVER_HOST = "3.131.207.170"
    MID_CONN_SERVER_PORT = 12384
    RECV_BUFF_SIZE = 2048

    def __init__(self):
        self.__socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP
        )

        self.__socket.connect((ServerConnection.MID_CONN_SERVER_HOST, ServerConnection.MID_CONN_SERVER_PORT))

    def send_packet(self, packet: BasePacket) -> ServerResponsePacket:
        """ Отправляет пакет с командами.

        :param packet - Экземпляр класса CommandPacket,
        предварительно сформированный при помощи его методов.
        """
        self.__socket.send(packet.convert_to_packet_bytes())

        response = ServerResponsePacket(self.__socket.recv(ServerConnection.RECV_BUFF_SIZE))

        return response


def main():
    """ Основное окружение администратора, предназначенное
     для отправки комманд на выполнение хостам пула.
    """
    print(f"\n[{colored('+', 'green')}] Вы успешно вошли в личный кабинет.")
    print(f"\n[{colored('?', 'yellow')}] Получение данных о хостах, находящихся в пуле...")

    while True:
        # TODO: Реализовать интерфейс ввода комманд и дальнейшую их пересылку хосту.
        pass


if __name__ == "__main__":
    print(r"""   ___ ___  ___ ___     _   ___  __  __ ___ _  _ 
  / __| _ \/ __/ __|   /_\ |   \|  \/  |_ _| \| |
 | (__|   / (__\__ \  / _ \| |) | |\/| || || .` |
  \___|_|_\\___|___/ /_/ \_\___/|_|  |_|___|_|\_|
    
                   @ AUTHORS @
         https://github.com/SepultureSE
           https://github.com/Kaseki1
    """)

    try:
        # Если ошибка в классе Session не возникает, то переключает на функцию main(),
        # где реализуется интерфейс отправки комманд хостам.
        Session()
        main()
    except SessionDirectoryError as error:
        # если сессия не обнаружена, то обязует зарегистрировать
        # или авторизовать личный кабинет.
        choice = input(f"[{colored('?', 'yellow')}] Активных сессий не найдено."
                       f"\n[{colored('?', 'yellow')}] Войдите в аккаунт(1) или Зарегистрируйтесь(2): ")

        if choice.strip() == "1":
            print(f"[{colored('?', 'yellow')}] Введите данные от вашего личного кабинета.")

            while True:
                login = input("\nЛогин: ")
                password = input("Пароль: ")

                auth_packet = AuthPacket(login, password)
                connection = ServerConnection()
                response = connection.send_packet(auth_packet)

                if response.CODE == "success":
                    main()
                else:
                    print(f"\n[{colored('!', 'red')}] Неверный логин или пароль.")

        elif choice.strip() == "2":
            print(f"[{colored('?', 'yellow')}] Введите данные от вашего личного кабинета.")

            while True:
                login = input("\nЛогин: ")
                mail = input("Email: ")
                password = getpass.getpass("Пароль: ")
                password_confirmation = getpass.getpass("Повторите пароль: ")

                if password == password_confirmation:
                    registration_packet = RegistrationPacket(login, password, mail)
                    connection = ServerConnection()
                    response = connection.send_packet(registration_packet)

                    if response.CODE == "success":
                        main()
                else:
                    print(f"\n[{colored('!', 'red')}] Пароли не совпадают. Повторите введение данных учетной записи.")
