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


def get_files_from_directory(path, ext: str = None):
    if not exists_directory(path):
        return []

    if ext:
        assert isinstance(ext, str), f"ext must be string but {ext, type(ext)}"
        if not ext.startswith('.'):
            ext = '.' + ext
        return [f"{f.stem}{f.suffix}" for f in _Path(path).iterdir() if f.is_file() and f.suffix == ext]

    return [f"{f.stem}{f.suffix}" for f in _Path(path).iterdir() if f.is_file()]


def get_folders_from_directory(path):
    if not exists_directory(path):
        return []

    return [f"{f.stem}{f.suffix}" for f in _Path(path).iterdir() if f.is_dir()]


def get_file_name(path):
    return _Path(path).name


def get_file_extension(path):
    return _Path(path).suffix
