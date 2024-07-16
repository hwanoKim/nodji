import os


def exists_diectory(path):
    return os.path.exists(path) and os.path.isdir(path)


def exists_path(path):
    """폴더 파일 아무거나 존재하는지 확인"""
    return os.path.exists(path)


def make_directory(path):
    if not exists_diectory(path):
        os.makedirs(path)


def delete_directory(path):
    if exists_diectory(path):
        os.rmdir(path)


def get_file_name(path):
    return os.path.basename(path)


def get_file_extension(path):
    return os.path.splitext(path)[1]
