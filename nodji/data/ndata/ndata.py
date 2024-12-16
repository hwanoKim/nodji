"""
여기서 말하는 DataframeData은 저장단위로 이해하면 좋다.
하나의 데이터를 관리하는데
각각의 이름으로 정의하며 형식은 pd.DataFrame을 빌려온다.
"""
from typing import Optional

import nodji as nd
import pandas as pd

from loguru import logger
from ...core.ntime import NTime
from .ndata_save import NDataSaverBase
from .ndata_load import NDataLoaderBase


class NData:
    """데이터를 저장하는 클래스.

    설명:
        특징:
            데이터는 이름으로 구분한다.
            내부에서는 NDataFrame을 기반으로 한다.
            이름을 기준으로 Data가 정의 되는데 Data의 instance를 생성해도
            자동으로 load하거나 하지는 않는다.
            instance만 생성하고 필요할때만 실제 데이터를 읽는다.

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

        왜 NDataFrame과 통일하지 않았나?
            현재는 NData -> NDataFrame의 구조로 되어 있다.
            언듯보면 그냥 NData로 두개를 통합해도 되지 않나 싶다.
            다음과 같은 구조에서 문제가 된다.
                PriceData는 NData를 상속받아서 사용한다.
                NData내에서 옛날 데이터를 복사해서 새로운 데이터와 병합하는 등의 과정을
                거쳐야 한다. 하지만 현재는 NData라는 것은 name을 기준으로 구분되도록 되어 있다.
                그렇기 때문에 NData를 복사해서 병합할때 하나의 이름을 가진 여러개의
                instance가 생기게 된다. 따라서 이름을 기준으로 하는
                NData와 병합등의 과정을 담당할 NDataFrame을 분리하였다.
    """

    def __init__(self, name: str):
        self._name = name
        self._ndf = nd.NDataFrame()

    def __repr__(self):
        return self._ndf.__repr__()

    def __add__(self, other):
        """데이터를 더한다."""
        if isinstance(other, nd.NDataFrame):
            self._ndf += other
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
    def is_empty(self):
        return self._ndf.is_empty

    @property
    def save_path(self):
        """현재의 데이터를 기반으로 저장할 경로를 반환한다."""
        if isinstance(self._df.index, pd.DatetimeIndex):
            return nd.Paths.DATABASE / f"{self.name}"
        else:
            return nd.Paths.DATABASE / f"{self.name}.{nd.consts.Extensions.NDATAFRAME}"

    @property
    def cols(self) -> list[str]:
        """column의 이름을 리스트로 반환한다."""
        return self._df.columns.tolist()

    @cols.setter
    def cols(self, value):
        """column의 이름을 설정한다."""
        self._df.columns = value

    @property
    def start_time(self):
        return self._ndf.start_time

    @start_time.setter
    def start_time(self, value):
        self._ndf.start_time = value

    @property
    def end_time(self):
        return self._ndf.end_time

    @end_time.setter
    def end_time(self, value):
        self._ndf.end_time = value

    def load(self) -> 'nd.NDataFrame':
        """읽어온다. 없으면 빈 데이터프레임을 반환한다."""
        for cls in NDataLoaderBase.__subclasses__():
            if cls.has_matching_file(self.name):
                self._ndf = cls(self).load()
                logger.info(f"{self.name}'s ndata loaded")
                return self._ndf
        return nd.NDataFrame()

    def copy_ndataframe(self) -> 'nd.NDataFrame':
        return self._ndf.copy()

    def set_ndataframe(self, ndataframe: 'nd.NDataFrame'):
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
        """
        assert isinstance(ndataframe, nd.NDataFrame), f"ndataframe must be NDataFrame but {type(ndataframe)}"
        self._ndf = ndataframe
        return self

    def save(self):
        for cls in NDataSaverBase.__subclasses__():
            if cls.is_match(self._ndf):
                cls(self).save()
                logger.info(f"{self.name}'s ndata saved")
                return


class NDataIndex:
    """NData의 index를 관리하는 클래스.

    설명:
    """

    def __init__(self, index: pd.Index):
        self._index = index
