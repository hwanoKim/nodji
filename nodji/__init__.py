import sys

from loguru import logger
from .core.types import LogLevel, TimeZone


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

from .core.ntime import NTime
from .core.os_utils import *
from .core.dataframe import *
from .assets import Assets
from .core import constants as consts
from .core.paths import Paths
from .trading.upbit import Upbit
from .data.ndata.ndata import NData, NTimeSeriesData
from .data.analyzer.price_data_analyzer import CoinPriceDataAnalyzer
from .backtester.backtester import CoinBacktester, BacktestConfig
from .backtester.evaluators import evaluators
from .backtester.indicators import indicators
from .utils.email import Email
from .utils.lotto import email_lotto_numbers, Lotto
