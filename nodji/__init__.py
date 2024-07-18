import sys

from loguru import logger
from .common.types import *


def _custom_formatter(record):
    record["extra"]["shortname"] = record["name"].split(".")[-1]
    return "| {level:<5} | {extra[shortname]:<9}- {line:<3} | {message:<100} | {time:YYYY-MM-DD HH:mm:ss.SSS} \n"


def set_log_level(level: LogLevel):
    if not isinstance(level, LogLevel):
        raise TypeError('level should be LogLevel')
    logger.remove()
    logger.add(
        sys.stdout,
        format=_custom_formatter,
        level=str(level.name),
        enqueue=False,
        colorize=True
    )


set_log_level(LogLevel.WARNING)

from .assets import Assets
from .common import constants as consts
from .common.paths import Paths
from .common.file_utils import *
from . import external_apis
from .data.datarame_data import DataFrameData

