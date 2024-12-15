from pathlib import Path as _Path


def exists_directory(path):
    return _Path(path).exists() and _Path(path).is_dir()


def exists_path(path):
    """폴더 파일 아무거나 존재하는지 확인"""
    return _Path(path).exists()


def make_directory(path):
    if not exists_directory(path):
        _Path(path).mkdir(parents=True)


def delete_directory(path):
    if exists_directory(path):
        _Path(path).rmdir()


def get_file_name(path):
    return _Path(path).name


def get_file_extension(path):
    return _Path(path).suffix
