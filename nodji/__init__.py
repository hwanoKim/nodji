import sys

from loguru import logger
from .common.types import *


def _custom_formatter(record):
    record["extra"]["shortname"] = record["name"].split(".")[-1]
    return "| {level:<5} | {message:<100} | {extra[shortname]:<20}- {line:<5} | {time:YYYY-MM-DD HH:mm:ss.SSS} \n"


def log(level: LogLevel, output_to_file: bool = False, file_path: str = None):
    assert isinstance(level, LogLevel), 'level should be LogLevel'
    logger.remove()
    if output_to_file:
        if file_path is None:
            file_path = Paths.MODULE + '/log.log'
        logger.add(file_path, format=_custom_formatter, level=str(level.name), rotation="10 MB")
    else:
        logger.add(
            sys.stdout,
            format=_custom_formatter,
            level=str(level.name),
            enqueue=False,
            colorize=True)


log(LogLevel.WARNING)

from .assets import Assets
from .common import constants as consts
from .common.paths import Paths
from .common.dataframe import *
from .common.file_utils import *
from .common.ntime import NTime
from . import external_apis
from nodji.data.dataframe_data.datafame_data import DataFrameData
from .utils.emailUtil import Email
from .utils.lotto import email_lotto_numbers
