from pathlib import Path
from typing import Union, Generator, Optional
from ...core.file_utils import exists_path
from .ndata_load import NDataLoaderBase
from .ndata_save import NDataSaverBase
import pandas as pd
import nodji as nd
from loguru import logger


class NData:
    """데이터를 저장하는 클래스.

    설명:
        pd.DataFrame을 기반으로 한다.
            내부의 pd.DataFrame을 최대한 사용자가 직접 다루지 않게 하기 위해서 만들었다.
            머리가 멍청해서 pd.DataFrame을 다루는데 매번 헷갈린다.
            그래서 pd.DataFrame을 내부로 숨기고 내가 이해하기 위한 방식으로 wrapping하였다

        데이터의 구분은 이름으로 한다.
            데이터는 이름으로 구분한다.
            이름을 기준으로 Data가 정의 되는데 Data의 instance를 생성해도
            자동으로 load하거나 하지는 않는다.
            instance만 생성하고 필요할때만 실제 데이터를 읽는다.

        nodji의 모든 데이터의 원형이다
            nodji에서의 데이터들 예를 들어 assetsData, priceData 모두 이 NData를 원형으로 한다

        확장자:
            결국 실제 저장은 최종적으로 DataFrame을 저장하기 때문에
            개별적 파일은 .df로 저장한다.

        저장 / 불러오기:
            이름을 기반으로 하여 저장 / 불러오기 기능을 포함하였다.
            이름으로한 경로가 자동으로 지정된다.

        시간 단위의 개념
            또한 저장할 때 자동으로 너무 긴 시계열의 데이터를 분할 저장, 불러오기의 기능도 함께 한다.
            시계열 index를 가지는 데이터라면 시간 단위에 따라서 분할 한다.
            예를 들어 index가 분당인 데이터는 Monlty로 저장한다.
            index가 일단위 데이터는 Yearly로 저장한다.
    """

    def __init__(self, name: str):
        self._name = name
        self._df = pd.DataFrame()

    def __repr__(self):
        return self._df.__repr__()

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

    def __getattr__(self, item):
        return getattr(self._df, item)

    def __getitem__(self, item):
        return self._df[item]

    def __setitem__(self, key, value):
        self._df[key] = value

    def __call__(self, df: pd.DataFrame):
        self._df = df
        return self

    @property
    def name(self):
        return self._name

    @property
    def exists(self):
        for cls in NDataLoaderBase.__subclasses__():
            if cls.has_matching_file(self.name):
                return True
        else:
            return False

    @property
    def save_path(self):
        """현재의 데이터를 기반으로 저장할 경로를 반환한다."""
        if isinstance(self._df.index, pd.DatetimeIndex):
            return nd.Paths.DATABASE / f"{self.name}"
        else:
            return nd.Paths.DATABASE / f"{self.name}.{nd.consts.Extensions.NDATA}"

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

    def load(self) -> 'NData':
        """읽어온다.

        설명:
            DB폴더안에 해당이름이 없으면 패스
        """
        if self.name not in self._get_all_data_names():
            return self
        for cls in NDataLoaderBase.__subclasses__():
            if cls.has_matching_file(self.name):
                self._df = cls(self).load()
                logger.info(f"{self.name}'s ndata loaded")
                return self
        else:
            raise ValueError(f"no matching file for {self.name}")

    def copy_dataframe(self) -> pd.DataFrame:
        return self._df.copy()

    def set_dataframe(self, dataframe: pd.DataFrame) -> 'NData':
        """ndata에 데이터프레임을 설정한다."""
        assert isinstance(dataframe, pd.DataFrame), f"dataframe type must be pd.DataFrame but {type(dataframe)}"
        self._df = dataframe
        return self

    def save(self):
        for cls in NDataSaverBase.__subclasses__():
            if cls.is_match(self._df):
                cls(self).save()
                logger.info(f"{self.name}'s ndata saved")
                return

    def _get_all_data_names(self) -> list[str]:
        data_names = []
        for cls in NDataLoaderBase.__subclasses__():
            data_names += cls.get_all_data_names()
        return data_names


class NDataIndex:
    """NData의 index를 관리하는 클래스.

    설명:
        todo: 이건 만들다 말아서 현재 기억이 안난다
    """

    def __init__(self, index: pd.Index):
        self._index = index
