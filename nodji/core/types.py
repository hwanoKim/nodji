from enum import Enum, auto
from zoneinfo import ZoneInfo


class LogLevel(Enum):
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


class DataStorageFrequency(Enum):
    DAILY = auto()
    WEEKLY = auto()
    MONTHLY = auto()
    ANNUALLY = auto()


class TimeZone(Enum):
    SEOUL = ZoneInfo("Asia/Seoul")
    UTC = ZoneInfo("UTC")
