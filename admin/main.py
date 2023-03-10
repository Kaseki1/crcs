from termcolor import colored
import tabulate
import getpass
import socket
import json
import os
import pathlib
import abc


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
    SESSION_DIR = pathlib.Path("/var/tmp/crcs_session/")  # TODO: Сделать вариант пути для Windows и MacOS.

    if not SESSION_DIR.exists():
        SESSION_DIR.mkdir()

    def __init__(self):
        files_in_session_directory = os.listdir(Session.SESSION_DIR)

        if len(files_in_session_directory) > 1:
            raise SessionDirectoryError("В директории админских сессий было обнаружено более одного файла.")

            # При обнаружении нескольких файлов сессий в директории -
            # удаляет их из директории.
            for file in files_in_session_directory:
                Session.SESSION_DIR.joinpath(file).unlink()

        elif len(files_in_session_directory) == 0:
            raise SessionDirectoryError("Сессия отсутствует.")
        else:
            self.__sessionuid = files_in_session_directory[0]

    @property
    def last_hostname(self):
        with open(Session.SESSION_DIR.joinpath(self.__sessionuid), "rb") as fp:
            session_json_data = json.load(fp)

        return session_json_data["last_hostname"]

    @last_hostname.setter
    def last_hostname(self, value):
        with open(Session.SESSION_DIR.joinpath(self.__sessionuid), "r") as fp:
            session_json_data = json.load(fp)

        with open(Session.SESSION_DIR.joinpath(self.__sessionuid), "w") as fp:
            session_json_data["last_hostname"] = value
            json.dump(session_json_data, fp)

    @property
    def mode(self):
        with open(Session.SESSION_DIR.joinpath(self.__sessionuid), "rb") as fp:
            session_json_data = json.load(fp)

        return session_json_data["mode"]

    @mode.setter
    def mode(self, value):
        with open(Session.SESSION_DIR.joinpath(self.__sessionuid), "r") as fp:
            session_json_data = json.load(fp)

        with open(Session.SESSION_DIR.joinpath(self.__sessionuid), "w") as fp:
            session_json_data["mode"] = value
            json.dump(session_json_data, fp)

    @property
    def last_pool_id(self):
        with open(Session.SESSION_DIR.joinpath(self.__sessionuid), "rb") as fp:
            session_json_data = json.load(fp)

        return session_json_data["last_pool_id"]

    @last_pool_id.setter
    def last_pool_id(self, value):
        with open(Session.SESSION_DIR.joinpath(self.__sessionuid), "r") as fp:
            session_json_data = json.load(fp)

        with open(Session.SESSION_DIR.joinpath(self.__sessionuid), "w") as fp:
            session_json_data["last_pool_id"] = value
            json.dump(session_json_data, fp)

    def get_session_uid(self):
        return self.__sessionuid

    def remove(self):
        """ Удаляет файл сессии """
        Session.SESSION_DIR.joinpath(str(self.__sessionuid)).unlink()

    @staticmethod
    def save_session(session_uid: str):
        """ Сохраняет файл сессии в директорию админской сессии """
        session_file_struct = {
            "mode": "broadcast",
            "last_hostname": None,
            "last_pool_id": None
        }

        with open(Session.SESSION_DIR.joinpath(session_uid), "w") as fp:
            json.dump(session_file_struct, fp)


class BasePacket(abc.ABC):
    """ Базовый класс всех пакетов """

    def __init__(self):
        self._operation_type: str  # Указывает формат пакета

    @abc.abstractmethod
    def convert_to_packet_bytes(self) -> bytes:
        """ Конвертирует объект пакета в поток байт """
        pass


class UnicastPacket(BasePacket):
    """ Класс пакета команды, которую должен выполнить клиент.
    Используется в методах отправки данных на сервер.
    """
    def __init__(self, command: str = None, receiver: str = None, session: Session = None):
        super().__init__()

        if not session:
            session = Session()

        self._operation_type = "command"
        self.command: str = command      # Команда, которую должен исполнить клиент
        self.receiver: str = receiver    # Идентификатор хоста
        self.session: Session = session  # Идентификатор сессии текущего администратора

    def convert_to_packet_bytes(self) -> bytes:
        """ Формирует пакет для отправки по сети,
        основанный на json, используя атрибуты текущего
        экземпляра пакета """
        packet = {
            "op_type": self._operation_type,
            "command": None,
            "receiver": None,
            "sessionuid": None,
            "pool_id": None
        }

        # Далее идет проверка введение полей пакета.
        if self.command:
            packet["command"] = self.command
        else:
            raise PacketFormatError("Required package parameter \"command\" was not filled.")

        if self.session:
            packet["sessionuid"] = self.session.get_session_uid()
        else:
            raise PacketFormatError("Required package parameter \"sessionuid\" was not filled.")

        if self.receiver:
            packet["receiver"] = self.receiver
        else:
            raise PacketFormatError("Required package parameter \"receiver\" was not filled.")

        return json.dumps(packet).encode("utf8")


class BroadcastPacket(BasePacket):
    """ Класс пакета команды, которую должен выполнить клиент.
    Используется в методах отправки данных на сервер.
    """

    def __init__(self, command: str = None, pool_id: int = None, session: Session = None):
        super().__init__()

        if not session:
            session = Session()

        self._operation_type = "command"
        self.command: str = command      # Команда, которую должен исполнить клиент
        self.session: Session = session  # Идентификатор сессии текущего администратора
        self.pool_id: int = pool_id      # Идентификатор пула

    def convert_to_packet_bytes(self) -> bytes:
        """ Формирует пакет для отправки по сети,
        основанный на json, используя атрибуты текущего
        экземпляра пакета """
        packet = {
            "op_type": self._operation_type,
            "command": None,
            "receiver": "broadcast",
            "sessionuid": None,
            "pool_id": None
        }

        # Далее идет проверка введение полей пакета.
        if self.command:
            packet["command"] = self.command
        else:
            raise PacketFormatError("Required package parameter \"command\" was not filled.")

        if self.session:
            packet["sessionuid"] = self.session.get_session_uid()
        else:
            raise PacketFormatError("Required package parameter \"sessionuid\" was not filled.")

        if self.pool_id:
            packet["pool_id"] = self.pool_id
        else:
            raise PacketFormatError("Required package parameter \"pool_id\" was not filled.")

        return json.dumps(packet).encode("utf8")


class AuthPacket(BasePacket):
    """ Реализация формата пакета для аутентификации
    личного кабинета администратора сети.
    """

    def __init__(self, login: str = None, password: str = None):
        super().__init__()

        self._operation_type = "auth"
        self.login: str = login  # Логин личного кабинета администратора
        self.password: str = password  # Пароль личного кабинета администратора

    def convert_to_packet_bytes(self) -> bytes:
        packet_json_format = {
            "op_type": self._operation_type,
            "login": None,
            "password": None
        }

        if self.login:
            packet_json_format["login"] = self.login
        else:
            raise PacketFormatError("Required package parameter \"login\" was not filled.")

        if self.password:
            packet_json_format["password"] = self.password
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
        self.login: str = login        # Логин личного кабинета администратора
        self.password: str = password  # Пароль личного кабинета администратора
        self.email: str = email        # Почта администратора

    def convert_to_packet_bytes(self) -> bytes:
        packet_json_format = {
            "op_type": self._operation_type,
            "login": None,
            "password": None,
            "email": None
        }

        if self.login:
            packet_json_format["login"] = self.login
        else:
            raise PacketFormatError("Required package parameter \"login\" was not filled.")

        if self.password:
            packet_json_format["password"] = self.password
        else:
            raise PacketFormatError("Required package parameter \"password\" was not filled.")

        if self.email:
            packet_json_format["email"] = self.email
        else:
            raise PacketFormatError("Required package parameter \"email\" was not filled.")

        return json.dumps(packet_json_format).encode("utf8")


class ServerPacket(BasePacket):
    """ Реализует формат пакета,
     адресованного центральному серверу.
    """

    def __init__(self, request: str = None, additional_data: str = None, session: Session = None):
        super().__init__()

        if not session:
            session = Session()

        self._operation_type = "server"
        self.request: str = request
        self.session: Session = session
        self.additional_data: str = additional_data

    def convert_to_packet_bytes(self) -> bytes:
        packet_json_format = {
            "op_type": self._operation_type,
            "request": None,
            "additional_data": self.additional_data,
            "sessionuid": None
        }

        if self.request:
            packet_json_format["request"] = self.request
        else:
            raise PacketFormatError("Required package parameter \"request\" was not filled.")

        if self.session:
            packet_json_format["sessionuid"] = self.session.get_session_uid()
        else:
            raise PacketFormatError("Required package parameter \"sessionuid\" was not filled.")

        return json.dumps(packet_json_format).encode("utf8")


class ResponseHandler:
    """ ООП представление пакета ответа сервера.
    Возвращается в классе ServerConnection.
    """
    def __init__(self, response: bytes):
        data = json.loads(response)

        self.COMMENT = data["comment"]
        self.DATA = data["data"]

        if data["code"] == "success":
            self.IS_SUCCESS = True
        else:
            self.IS_SUCCESS = False


class ServerConnection:
    """ Класс подключения к серверу """
    MID_CONN_SERVER_HOST = "18.178.86.139"
    MID_CONN_SERVER_PORT = 9090
    RECV_BUFF_SIZE = 16384
    TERMINATOR = b"\x04"

    def __init__(self):
        self.__socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP
        )

        self.__socket.connect((ServerConnection.MID_CONN_SERVER_HOST, ServerConnection.MID_CONN_SERVER_PORT))

    def send_packet(self, packet: BasePacket) -> ResponseHandler:
        """ Отправляет пакет с командами.

        :param packet - Экземпляр класса CommandPacket,
        предварительно сформированный при помощи его методов.
        """
        self.__socket.send(packet.convert_to_packet_bytes() + ServerConnection.TERMINATOR)
        response = self.__socket.recv(ServerConnection.RECV_BUFF_SIZE)
        packet = ResponseHandler(response)
        self.__socket.close()

        return packet


def main():
    """ Основное окружение администратора, предназначенное
     для отправки комманд на выполнение хостам пула.
     Реализация пользовательского интерфейса.
    """
    print(f"\n[{colored('+', 'green')}] Вы успешно вошли в личный кабинет.")

    # --СЕКЦИЯ ПЕРЕМЕННЫХ ТЕКУЩЕЙ СЕССИИ--
    # Подгрузка переменных текущей сессии из файла сессии.
    session = Session()

    COMMAND_SCOPE = session.mode            # Текущее окружение команд: Unicast, Broadcast, Multicast.
    COMMAND_TARGET = None                  # Цель команды (хост). Нужна в случае с Unicast и Multicast.
    SAVED_HOST_ID = None                   # В эту переменную сохраняется HOST_ID после выполнения команды Unicast.
    INVITATION = "\n[None]$ "              # Приглашение ввода команды

    while True:
        command = input(INVITATION).strip()
        # в ветвлении идет обработка команд, которые не должны отсылаться
        # на сервер или должны формировать пакеты, отличные от пакетов команд
        # (например пакеты запросов непосредственно на центральный сервер).

        # -------------------------------------------------------------------------------------------------------
        # [[ Локальные команды ]]
        if command == "logout":
            session.remove()
            print(f"[{colored('?', 'yellow')}] Вы вышли из личного кабинета.\n")
            exit(0)

        elif command == "help":
            print(f"""[{colored('?', 'yellow')}] Список команд админской панели.
Последнее обновление: 12.09.2022\n
[[ РЕЖИМЫ ОТПРАВКИ ПАКЕТОВ ]] 
* unicast (host_id) - Переключается на отправку команд хосту с ID (host_id).
* broadcast (pool_id) - Отправляет команды всем хостам в пуле с номером (pool_id).

[[ УПРАВЛЕНИЕ ПУЛОМ ]]
* pool create - Создает новый пул. Чтобы узнать его номер, введите следующую команду.
* pool members - Выводит список всех участников во всех админских пулах.
* pool delete (pool_id) - Удаляет пул с номером (pool_id).

[[ КОМАНДЫ УТИЛИТЫ "FS" ]]
* fs pwd - Возвращает текущий путь хоста.
* fs cd (path) - Меняет текущий путь хоста на (path).
* fs ls - Возвращает список всех файлов в текущем каталоге. 
* fs rm (path) - Удаляет файл, находящийся по адресу (path).
* fs cat (path) - Возвращает содержимое файла, находящегося по адресу (path).

[[ КОМАНДЫ УТИЛИТЫ "SH" ]]
* sh (command) - выполняет команду удаленного shell`а.""")
        # -------------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------------
        # [[ Переключение между режимами Unicast, Broadcast, Multicast ]]
        # TODO: Заменить механизм Unicast (прохода по двум циклам всех хостов для формирования LOCAL_HOST_UID) на
        # запрос к серверу HOST_ID_BY_HOSTNAME.
        elif command.startswith("unicast "):
            connection = ServerConnection()

            try:
                target = command[8::]
            except ValueError:
                print(f"[{colored('-', 'red')}] Неверный формат аргумента. Введите номер пула, состоящий из числа.")

            pools = connection.send_packet(ServerPacket(
                request="GET_ADMIN_POOLS"
            )).DATA

            for pool in pools:
                connection = ServerConnection()
                pool_members = connection.send_packet(ServerPacket(
                    request="GET_POOL_MEMBERS",
                    additional_data=pool
                )).DATA

                for member in pool_members:
                    if member["hostname"] == target:
                        COMMAND_SCOPE = "unicast"
                        COMMAND_TARGET = member["hostname"]
                        SAVED_HOST_ID = member["host_id"]

                        try:
                            connection = ServerConnection()
                            current_path = connection.send_packet(UnicastPacket("fs pwd", SAVED_HOST_ID)).DATA

                            INVITATION = f"[{COMMAND_TARGET} {current_path}] "
                            print(f"[{colored('+', 'green')}] Режим переключен на Unicast: {COMMAND_TARGET}\n")
                            break
                        except:
                            print(f"[{colored('-', 'red')}] Хостнейм отключен от сервера.")
                            break
                else:
                    # если не найдено, то сообщает об ошибке поиска.
                    print(f"[{colored('-', 'red')}] Хостнейм не был найден.")

        elif command.startswith("broadcast "):
            connection = ServerConnection()
            target = command.split(" ")[1]

            print(f"[{colored('?', 'yellow')}] Получение базы админских пулов...")
            admin_pools = connection.send_packet(ServerPacket("GET_ADMIN_POOLS"))

            if admin_pools.IS_SUCCESS:
                print(f"[{colored('+', 'green')}] Транзакция получения успешна.")
                print(f"[{colored('?', 'yellow')}] Проверка на существование пула в базе.")

                if int(target) in admin_pools.DATA:
                    COMMAND_SCOPE = "broadcast"
                    COMMAND_TARGET = None
                    INVITATION = "\n[broadcast]$ "

                    print(f"[{colored('+', 'green')}] Режим успешно был сменен на BROADCAST.")
                else:
                    print(f"[{colored('-', 'red')}] Указаного пула не существует.")
            else:
                print(f"[{colored('-', 'red')}] Ошибка транзакции.")
        # -------------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------------
        # [[ РЕАЛИЗАЦИЯ УТИЛИТЫ POOL ]]
        # На эту утилиту не влияет область исполнения команд.
        elif command == "pool members":
            connection = ServerConnection()
            pools = connection.send_packet(ServerPacket("GET_ADMIN_POOLS")).DATA

            if not pools:
                print(f"[{colored('?', 'yellow')}] Вы еще не создали ни один пул. "
                      f"Воспользуйтесь командой \"pool create\".")
            else:
                # получает всех пользователей в полученных пулах и
                # сортирует их по массиву для вывода информации.
                for pool in pools:
                    connection = ServerConnection()
                    print(f"[{colored('?', 'yellow')}] Вывод информации об участниках пула №{pool}.")
                    request = ServerPacket("GET_POOL_MEMBERS", additional_data=pool)
                    hosts = connection.send_packet(request).DATA

                    if hosts:
                        for host in hosts:
                            # содержащий соответствие локального ID хоста, который будет использоваться в командах
                            # ID, который содержится в базе данных.
                            print(f"   {host['hostname']}")
                    else:
                        print("   В данный пул еще никто не вступил ...")

        elif command == "pool create":
            connection = ServerConnection()
            response = connection.send_packet(ServerPacket("CREATE_POOL"))

            if response.IS_SUCCESS:
                # TODO: Сделать так, чтобы сервер возвращался в поле DATA код нового созданного пула.
                print(f"[{colored('+', 'green')}] Был создан пул. Введите \"pool members\" для "
                      f"получения подробной информации о нем.")
            else:
                print(f"[{colored('-', 'red')}] Ошибка создания пула.")

        elif command == "pool delete ":
            connection = ServerConnection()
            response = connection.send_packet(ServerPacket("DESTROY_POOL", command.split(' ')[2]))

            if response.IS_SUCCESS:
                print(f"[{colored('+', 'green')}] Пул был успешно удален.")
            else:
                print(f"[{colored('-', 'green')}] Ошибка сервера: {response.COMMENT}")
        # -------------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------------
        # [[ РЕАЛИЗАЦИЯ УТИЛИТЫ FS ]]
        # P.S. Команды утилиты FS не могут использоваться при Broadcast запросах из-за
        # ненадобности такой реализации. На ПК хостов отличается директория, а вывод команд
        # cat, pwd.
        elif command.startswith("fs "):
            if COMMAND_SCOPE == "unicast":
                if command == "fs pwd":
                    connection = ServerConnection()
                    request_packet = UnicastPacket("fs pwd", SAVED_HOST_ID)
                    response = connection.send_packet(request_packet).DATA
                    print(f"[{colored('?', 'yellow')}] Текущий путь: {response}\n")

                elif command.startswith("fs cd "):
                    connection = ServerConnection()
                    request_packet = UnicastPacket(command, SAVED_HOST_ID)
                    response = connection.send_packet(request_packet).DATA

                    if response:
                        INVITATION = f"[{COMMAND_TARGET} {response}] "
                    else:
                        print(f"[{colored('-', 'red')}] Неверно задан удаленный путь.\n")

                elif command == "fs ls":
                    connection = ServerConnection()
                    request_packet = UnicastPacket(command, SAVED_HOST_ID)
                    response = connection.send_packet(request_packet).DATA

                    table_data = []

                    for file in response:
                        table_data.append([file["filename"], file["size"]])

                    table = tabulate.tabulate(table_data, headers=["Имя файла", "Размер"])
                    print(table)
                    print()

                elif command.startswith("fs rm "):
                    connection = ServerConnection()
                    request_packet = UnicastPacket(command, SAVED_HOST_ID)
                    response = connection.send_packet(request_packet).DATA

                    if response:
                        print(f"[{colored('+', 'green')}] Файл успешно удален.\n")
                    else:
                        print(f"[{colored('-', 'red')}] Файл не был найден.\n")

                elif command.startswith("fs cat "):
                    print(f"[{colored('?', 'yellow')}] Вывод содержимого файла: \"{command[7::]}\"")
                    connection = ServerConnection()
                    request_packet = UnicastPacket(command, SAVED_HOST_ID)
                    response = connection.send_packet(request_packet).DATA

                    if response:
                        print(response)
                    else:
                        print(f"[{colored('-', 'red')}] Файл не был найден.\n")
                else:
                    print(f"[{colored('!', 'red')}] Неизвестная команда. Повторите попытку.")
            else:
                print(f"[{colored('!', 'red')}] Утилиту \"fs\" возможно использовать только в режиме Unicast.")
        # -------------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------------
        # [[ РЕАЛИЗАЦИЯ УТИЛИТЫ SH ]]
        elif command.startswith("sh "):
            connection = ServerConnection()
            request_packet = UnicastPacket(command, SAVED_HOST_ID)
            response = connection.send_packet(request_packet).DATA
            print(response)
        # -------------------------------------------------------------------------------------------------------

        # В остальном случае, если команда не соответствует
        # никакой из реализаций утилит: локальная ошибка.
        else:
            print(f"[{colored('!', 'red')}] Неизвестная команда. Повторите попытку.\n")


if __name__ == "__main__":
    print(r"""   ___ ___  ___ ___     _   ___  __  __ ___ _  _ 
  / __| _ \/ __/ __|   /_\ |   \|  \/  |_ _| \| |
 | (__|   / (__\__ \  / _ \| |) | |\/| || || .` |
  \___|_|_\\___|___/ /_/ \_\___/|_|  |_|___|_|\_|
    
                   @ AUTHORS @
         https://github.com/SepultureSE
           https://github.com/Kaseki1""")

    try:
        # Если ошибка в классе Session не возникает ошибка об отсутствии файла,
        # то переключает на функцию main(),
        # где реализуется интерфейс отправки комманд хостам.
        session = Session()  # <- Глобальная переменная, которая используется в функции main()
        main()
    except SessionDirectoryError as error:
        # если сессия не обнаружена, то обязует зарегистрировать
        # или авторизовать личный кабинет.
        choice = input(f"\n[{colored('?', 'yellow')}] Активных сессий не найдено."
                       f"\n[{colored('?', 'yellow')}] Войдите в аккаунт(1) или Зарегистрируйтесь(2): ")

        # Реализация ВХОДА в личный кабинет.
        if choice.strip() == "1":
            print(f"[{colored('?', 'yellow')}] Введите данные от вашего личного кабинета.")

            while True:
                login = input("\nЛогин: ")
                password = input("Пароль: ")

                auth_packet = AuthPacket(login, password)
                connection = ServerConnection()
                response = connection.send_packet(auth_packet)

                if response.IS_SUCCESS:
                    Session.save_session(response.DATA)
                    session = Session()
                    main()
                else:
                    print(f"\n[{colored('!', 'red')}] Неверный логин или пароль.")

        # Реализация РЕГИСТРАЦИИ личного кабинета.
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

                    if response.IS_SUCCESS:
                        # После успешной регистрации отсылается пакет аутентификации,
                        # чтобы получить SESSION UID администратора и сохранить его.
                        auth_packet = AuthPacket(login, password)
                        connection = ServerConnection()
                        response = connection.send_packet(auth_packet)

                        Session.save_session(response.DATA)

                        main()
                    else:
                        print(f"\n[{colored('!', 'red')}] Ошибка регистрации: {response.COMMENT}")
                else:
                    print(f"\n[{colored('!', 'red')}] Пароли не совпадают. Повторите введение данных учетной записи.")
