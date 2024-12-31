import nodji as nd
import pandas as pd

from loguru import logger
from ...core.ntime import NTime
from .ndata_save import NDataSaverBase
from .ndata_load import NDataLoaderBase

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.ntime import NTime


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
            언뜻보면 그냥 NData로 두개를 통합해도 되지 않나 싶다.
            다음과 같은 구조에서 문제가 된다.
                PriceData는 NData를 상속받아서 사용한다.
                NData내에서 옛날 데이터를 복사해서 새로운 데이터와 병합하는 등의 과정을
                거쳐야 한다. 하지만 현재는 NData라는 것은 name을 기준으로 구분되도록 되어 있다.
                만약 같은 name을 가진 NData가 여러개 있다면 개념적으로 모두 동일한
                인스턴스여야한다.
                이러한 문제로 병합할때 문제가 된다.
                따라서 이름을 기준으로 하는 NData와 병합등의 과정을 담당할 NDataFrame을 분리하였다.
    """

    def __init__(self, name: str):
        self._name = name
        self._df = pd.DataFrame()

    def __repr__(self):
        return str(self._df)

    def __add__(self, other):
        """데이터를 더한다."""
        if isinstance(other, pd.DataFrame):
            self._df += other
            return self
        else:
            raise NotImplementedError(f"other must be pd.DataFrame but {type(other)}")

    def __contains__(self, item):
        if isinstance(item, NTime):
            if self._df.is_empty:
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
        """저장된 데이터가 존재하는가?

        설명:
            is_empty와 헷갈릴 수 있다.
                is_empty는 저장되어 있던 데이터가 존재 하지만
                비어있는지를 확인하는 것이다.
        """
        for cls in NDataLoaderBase.__subclasses__():
            if cls.has_matching_file(self.name):
                return True
        else:
            return False

    @property
    def is_empty(self):
        return self._df.empty

    @property
    def has_datetime_index(self):
        return isinstance(self._df.index, pd.DatetimeIndex)

    @property
    def path(self):
        """현재의 데이터를 기반으로 저장할 경로를 반환한다."""
        if self.has_datetime_index:
            return nd.Paths.DATABASE / self.name
        else:
            return nd.Paths.DATABASE / f"{self.name}.{nd.consts.Extensions.DATAFRAME}"

    @property
    def cols(self) -> list[str]:
        """column의 이름을 리스트로 반환한다."""
        return self._df.columns

    @cols.setter
    def cols(self, value):
        """column의 이름을 설정한다."""
        self._df.columns = value

    def load(self, start_time: 'NTime' = None, end_time: 'NTime' = None) -> 'pd.DataFrame':
        """읽어온다. 없으면 빈 데이터프레임을 반환한다."""
        for cls in NDataLoaderBase.__subclasses__():
            if cls.has_matching_file(self.name):
                self._df = cls(self).load(NTime(start_time), NTime(end_time))
                logger.info(f"{self.name}'s ndata loaded")
                return self._df
        return pd.DataFrame()

    def save(self):
        for cls in NDataSaverBase.__subclasses__():
            if cls.is_match(self):
                cls(self).save()
                logger.info(f"{self.name}'s ndata saved")
                return
        else:
            raise NotImplementedError(f"save method must be implemented in DataFrameDataSaverBase, {type(self)}")

    def set_dataframe(self, dataframe: pd.DataFrame):
        assert isinstance(dataframe, pd.DataFrame), f"dataframe must be pd.DataFrame but {type(dataframe)}"
        self._df = dataframe
        return self
