from pathlib import Path


class Paths:
    PROJECT = Path(__file__).resolve().parent.parent.parent
    MODULE = PROJECT / 'nodji'
    DATABASE = PROJECT / 'db'
