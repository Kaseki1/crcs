import os


def get_current_path() -> str:
    """ Получает текущий путь """
    return os.getcwd()


def change_path(path: str) -> str:
    """ Меняет текущий путь скрипта """
    os.chdir(path)
    return os.getcwd()


def get_file_list() -> list:
    """ Возвращает json массив с файлами и данными о них.
    Это нужно для того, чтобы реализовывать на админской стороне
    всеразличные Cli интерфейсы для взаимодействия с ФС.
    """
    result_dir_data = []

    # сортирует папки и файлы: сначала папки,
    # затем идут файлы.
    for file in os.listdir():
        if os.path.isdir(file):
            result_dir_data.append({
                "filename": file,
                "path": os.path.abspath(file),
                "is_file": True,
                "size": "DIR"
            })

    for file in os.listdir():
        if os.path.isfile(file):
            result_dir_data.append({
                "filename": file,
                "path": os.path.abspath(file),
                "is_file": True,
                "size": str(round(os.path.getsize(file) / 2048, 2)) + " MB"
            })

    return result_dir_data


def remove_file(path: str) -> None:
    """ Удаляет данный файл из директории """
    os.remove(path)


def get_file_content(path) -> str:
    """ Возвращает содержимое указанного файла """
    with open(path, "r") as fp:
        return fp.read(2048)
