from pathlib import Path as _Path
from typing import Union as _Union
from .ntime import NTime as _NTime

import pandas as _pd


def load_dataframe(path: _Union[str, _Path]) -> _pd.DataFrame:
    """데이터프레임을 불러온다.

    설명:
        데이터프레임을 불러온다.
    """
    return _pd.read_pickle(path)


def save_dataframe(dataframe: _pd.DataFrame, path: _Union[str, _Path]):
    """데이터프레임을 저장한다.

    설명:
        데이터프레임을 저장한다.
    """
    return dataframe.to_pickle(path)


def merge_dataframe_by_date(dataframe_1: _pd.DataFrame, dataframe_2: _pd.DataFrame) -> _pd.DataFrame:
    """데이터프레임을 날짜 기준으로 합친다.

    설명:
        데이터프레임을 날짜 기준으로 합친다.
    """
    return _pd.concat([dataframe_1, dataframe_2]).drop_duplicates().sort_index()


def find_duplicate_time_rows(dataframe: _pd.DataFrame) -> _pd.DataFrame:
    """데이터프레임에서 중복된 행을 찾는다.

    설명:
        데이터프레임에서 중복된 행을 찾는다.
    """
    duplicated_index = dataframe.index.duplicated(keep=False)
    return dataframe[duplicated_index]


def find_missing_time_ranges_of_dataframe(dataframe: _pd.DataFrame) -> list[tuple[_NTime, _NTime]]:
    """
    DataFrame의 DatetimeIndex에서 누락된 시간 구간을 반환합니다.

    Args:
        dataframe (pd.DataFrame): DatetimeIndex를 가진 DataFrame.

    Returns:
        list[tuple[pd.Timestamp, pd.Timestamp]]: 누락된 시간 구간의 리스트.
    """
    if dataframe.empty:
        return []

    index = dataframe.index
    if not isinstance(index, _pd.DatetimeIndex):
        raise ValueError(f"Expected a DataFrame with a DatetimeIndex, but got {type(index)}.")

    missing_ranges = []
    for i in range(1, len(index)):
        diff = (index[i] - index[i - 1]).total_seconds() / 60
        if diff > 1:
            start = index[i - 1] + _pd.Timedelta(minutes=1)
            end = index[i] - _pd.Timedelta(minutes=1)
            missing_ranges.append((_NTime(start), _NTime(end)))

    return missing_ranges
