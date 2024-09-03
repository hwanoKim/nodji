from pathlib import Path


def exists_directory(path):
    return Path(path).exists() and Path(path).is_dir()


def exists_path(path):
    """폴더 파일 아무거나 존재하는지 확인"""
    return Path(path).exists()


def make_directory(path):
    if not exists_directory(path):
        Path(path).mkdir(parents=True)


def delete_directory(path):
    if exists_directory(path):
        Path(path).rmdir()


def get_file_name(path):
    return Path(path).name


def get_file_extension(path):
    return Path(path).suffix
