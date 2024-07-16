from pathlib import Path as _Path


class Paths:
    PROJECT = _Path(__file__).resolve().parent.parent.parent
    MODULE = PROJECT / 'nodji'
    DATABASE = PROJECT / 'db'
