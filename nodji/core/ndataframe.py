from pathlib import Path
from typing import Union, Generator, Optional

import pandas as pd
from .file_utils import exists_path
import nodji as nd


class NDataFrame:
    """dataframe을 사용하기 쉽도록 만든 wrapper

    설명:
        내부의 pd.DataFrame을 최대한 사용자가 직접 다루지 않게 하기 위해서 만들었다.
        머리가 멍청해서 pd.DataFrame을 다루는데 매번 헷갈린다.
        그래서 pd.DataFrame을 내부로 숨기고 내가 이해하기 위한 방식으로 dataFrame을 형식을
        베이스로 한 data wrapper를 만들었다.
    """

    def __init__(self, df: pd.DataFrame = None):
        if df is None:
            df = pd.DataFrame()
        self._df = df

    def __repr__(self):
        return self._df.__repr__()

    def __add__(self, other):
        if isinstance(other, NDataFrame):
            self._df = pd.concat([self._df, other._df]).drop_duplicates()
            self._df.sort_index(inplace=True)
            return self
        else:
            raise NotImplementedError("other type must be NDataFrame")

    @property
    def is_empty(self):
        return self._df.empty

    @property
    def rows(self) -> Generator[pd.Series, None, None]:
        for _, row in self._df.iterrows():
            yield row

    @property
    def index(self) -> pd.Index:
        return self._df.index

    @property
    def start_time(self) -> nd.NTime:
        if isinstance(self._df.index, pd.DatetimeIndex):
            return nd.NTime(self._df.index[0])
        return nd.NTime(None)

    @start_time.setter
    def start_time(self, value):
        if isinstance(value, nd.NTime):
            self._df = self._df.loc[value._time:]
        else:
            raise NotImplementedError("value type must be NTime")

    @property
    def end_time(self) -> nd.NTime:
        if isinstance(self._df.index, pd.DatetimeIndex):
            return nd.NTime(self._df.index[-1])
        return nd.NTime(None)

    @end_time.setter
    def end_time(self, value):
        if isinstance(value, nd.NTime):
            self._df = self._df.loc[:value._time]
        else:
            raise NotImplementedError("value type must be NTime")

    def copy(self) -> 'NDataFrame':
        return NDataFrame(self._df.copy())

    def replace_dataframe(self, df: Union[pd.DataFrame, 'NDataFrame']) -> 'NDataFrame':
        """내부의 dataframe을 교체한다.

        설명:
            input으로 pd.DataFrame혹은 NDataFrame을 받을 수 있다.
        """
        if isinstance(df, NDataFrame):
            self._df = df._df
        elif isinstance(df, pd.DataFrame):
            self._df = df
        else:
            raise NotImplementedError(f"df type must be pd.DataFrame or NDataFrame but {type(df)}")
        return self

    def load_from_file(self, file_path: Union[str, Path]) -> 'NDataFrame':
        """파일에서 데이터를 불러온다.

        파일의 형식은 무조건 pickle로 저장되어 있어야 한다.
        """
        assert exists_path(file_path), f"file not found: {file_path}"
        if isinstance(file_path, str):
            file_path = Path(file_path)
        self._df = pd.read_pickle(str(file_path))
        return self

    def save_to_file(self, file_path: Union[str, Path]):
        """파일에 데이터를 저장한다.

        파일의 형식은 무조건 pickle로 저장된다.
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
        self._df.to_pickle(str(file_path))
