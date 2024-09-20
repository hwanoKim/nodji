"""
여기서 말하는 DataframeData은 저장단위로 이해하면 좋다.
하나의 데이터를 관리하는데
각각의 이름으로 정의하며 형식은 pd.DataFrame을 빌려온다.
"""
from pathlib import Path
from typing import Optional

import nodji as nd
import pandas as pd

from loguru import logger
from ...common.ntime import NTime
from .dataframe_data_saver import DataFrameDataSaverBase


class DataFrameData:
    """DataFrame 데이터를 저장하는 클래스

    Notes:
        내부의 pd.DataFrame을 최대한 사용자가 직접 다루지 않게 하기 위해서 만들었다.
            머리가 멍청해서 pd.DataFrame을 다루는데 매번 헷갈린다.
            그래서 pd.DataFrame을 내부로 숨기고 내가 이해하기 위한 방식을 통해서
            wrapper를 만들었다.

        시간 단위의 개념
            또한 저장할 때 자동으로 너무 긴 시계열의 데이터를 분할 저장, 불러오기의 기능도 함께 한다.
            일반 데이터와 분당 시간데이터가 있다.
            index가 시계열인 데이터는 Monlty로 저장한다.
            이것도 나중에는 직접 지정할 수 있어야 할것이다.
    """

    def __init__(self, name: str):
        self.name = name
        self._df = pd.DataFrame()

    def __repr__(self):
        return self._df.__repr__()

    def __call__(self, df: pd.DataFrame):
        """데이터프레임을 설정한다.

        Notes:
            기본 컨셉:
                nodji 안에서는 기본적으로 dataframe의 사용방법을 몰라도 되도록
                DataFrameData라는 클래스를 만들어서 dataframe 대용으로 사용하도록 한다.

            이름 혹은 경로:
                이름이든 path이든 사실 둘다 path를 지정하기 위한 방법 중 하나이다.
                둘중 하나의 방법을 사용하여 DataFrameData를 정의하여 사용하자.
                만약 불러오기 혹은 저장을 하지 않는 임시 DataFrameData를 만들수도 있다.
                그럴경우에는 이름 혹은 경로가 둘다 없을 수도 있다.

            __call__ 함수:
                dataframe 값을 적용하는 방법이다.
                마음같아서는
                    data = DataFrameData('name')
                    data = df

                이렇게 set을 하고 싶지만
                이렇게 되면 당연히 그냥 instance가 아닌 df로 변수가 교체되어버리므로
                set처럼 보이는 방법을 찾다가 __call__을 사용하게 되었다.
                    data = DataFrameData('name')
                    data(df)
        """
        assert isinstance(df, pd.DataFrame), f"df must be pd.DataFrame but {type(df)}"
        self._df = df
        return self

    def __add__(self, other):
        """데이터를 더한다."""
        if isinstance(other, pd.DataFrame):
            self._df = pd.concat([self._df, other]).drop_duplicates()
            self._df.sort_index(inplace=True)
            return self
        else:
            raise NotImplementedError(f"other must be pd.DataFrame but {type(other)}")

    def __contains__(self, item):
        if isinstance(item, NTime):
            if self._df.empty:
                raise ValueError("data is empty")
            else:
                start_time = self._df.index.min()
                end_time = self._df.index.max()
                return start_time <= item._time <= end_time
        else:
            raise NotImplementedError("item type must be NTime")

    @property
    def exists_file(self):
        for cls in DataFrameDataLoaderBase.__subclasses__():
            if cls.exists(self.name):
                return True
        else:
            return False

    @property
    def exists_data(self):
        return not self._df.empty

    @property
    def save_path(self):
        """현재의 데이터를 기반으로 저장할 경로를 반환한다."""
        if isinstance(self._df.index, pd.DatetimeIndex):
            return nd.Paths.DATABASE / f"{self.name}"
        else:
            return nd.Paths.DATABASE / f"{self.name}.{nd.consts.Extensions.DATAFRAME_DATA}"

    @property
    def cols(self) -> list[str]:
        """column의 이름을 리스트로 반환한다."""
        return self._df.columns.tolist()

    @cols.setter
    def cols(self, value):
        """column의 이름을 설정한다."""
        self._df.columns = value

    @property
    def start_time(self) -> Optional[nd.NTime]:
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
    def end_time(self) -> Optional[nd.NTime]:
        if isinstance(self._df.index, pd.DatetimeIndex):
            return nd.NTime(self._df.index[-1])
        return nd.NTime(None)

    @end_time.setter
    def end_time(self, value):
        if isinstance(value, nd.NTime):
            self._df = self._df.loc[:value._time]
        else:
            raise NotImplementedError("value type must be NTime")

    def load(self) -> pd.DataFrame:
        for cls in DataFrameDataLoaderBase.__subclasses__():
            if cls.exists(self.name):
                ins = cls(self)
                self._df = ins.load()
                logger.info(f"{self.name}'s dataframe loaded at {ins.path}")
                return self._df
        return pd.DataFrame()

    def copy(self) -> 'DataFrameData':
        new_data = DataFrameData(self.name)
        new_data(self._df.copy())
        return new_data

    def save(self):
        for cls in DataFrameDataSaverBase.__subclasses__():
            if cls.is_match(self._df):
                cls(self).save()
                logger.info(f"{self.name}'s dataframe saved at {self.path}")
                return
