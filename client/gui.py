import threading

from PyQt5 import QtWidgets, QtCore
from qttemplate import Ui_MainWindow
from client import *
from clientlib import *
import socket
import sys


class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFixedSize(422, 535)
        self.IS_HOST_FILE_EXISTS = False
        self.IS_ACCEPT_MODE = False

        # проверяет, подключен ли к пулу (существует ли файл host_id).
        try:
            host_id_file = HostUIDFile()
            self.IS_HOST_FILE_EXISTS = True
            self.ui.getPool.setText("Отключиться от пула")
            self.ui.lineEdit.setText(host_id_file.saved_hostname)
            self.ui.lineEdit.setDisabled(True)
        except HostUIDDirectoryError:
            # если файла нет
            self.ui.lineEdit.setText(socket.gethostname())
            self.ui.getPool.setText("Подключиться к пулу")

        self.ui.connectButton.clicked.connect(self.handle_connect_button)
        self.ui.getPool.clicked.connect(self.handle_admin_pool)

    def handle_connect_button(self):
        if self.IS_ACCEPT_MODE:
            self.IS_ACCEPT_MODE = False
            self.ui.connectButton.setText("Подключиться")
            self.success("Вы начали сессию обработки комманд.")
            self.ui.getPool.setDisabled(False)
        else:
            if self.IS_HOST_FILE_EXISTS:
                self.IS_ACCEPT_MODE = True
                self.__thread = threading.Thread(target=self.start_session)
                self.__thread.start()
                self.ui.connectButton.setText("Отключиться")
                self.success("Вы начали сессию обработки комманд.")
                self.ui.getPool.setDisabled(True)
            else:
                self.error("Вы еще не подключены ни к одному пулу.")

    def handle_admin_pool(self):
        if self.IS_HOST_FILE_EXISTS:
            try:
                connection = ServerConnection()
                connection.logout()
            except BaseException as exp:
                self.error(f"Ошибка: {exp}")
            else:
                self.success("Пул был успешно покинут.")
                self.ui.getPool.setText("Выберите админский пул")
                self.IS_HOST_FILE_EXISTS = False
                self.ui.lineEdit.setDisabled(False)
        else:
            text, ok = QtWidgets.QInputDialog.getText(self, "Подключение к пулу.", "Введите номер админского пула.")

            if ok:
                if text.isdigit():
                    try:
                        connection = ServerConnection()
                        result = connection.init_pool(int(text), self.ui.lineEdit.text())
                        host_id_file = HostUIDFile()
                        host_id_file.saved_hostname = self.ui.lineEdit.text()
                        self.ui.lineEdit.setDisabled(True)
                    except BaseException as ex:
                        self.error(f"Ошибка: {ex}")
                    else:
                        self.success(f"Вы успешно вступили в пул №{text}.")
                        self.IS_HOST_FILE_EXISTS = True
                        self.ui.getPool.setText("Отключиться от пула")
                else:
                    self.error("Номер пула должен являться числом, а не строкой.")

    def error(self, text: str):
        self.ui.textBrowser.append(f"<span style='color: red'>{text}</span><br/>")

    def success(self, text: str):
        self.ui.textBrowser.append(f"<span style='color: green'>{text}</span><br/>")

    def log(self, text: str):
        self.ui.textBrowser.append(f"{text}<br/>")

    def start_session(self):
        connection = ServerConnection()
        connection.start_session()

        while self.IS_ACCEPT_MODE:
            admin_command = connection.handle_commands(main_handler)
            self.log(f"> {admin_command}")


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    application = mywindow()
    application.show()

    sys.exit(app.exec())
