"""
여기서 말하는 DataframeData은 저장단위로 이해하면 좋다.
하나의 데이터를 관리하는데
각각의 이름으로 정의하며 형식은 pd.DataFrame을 빌려온다.
"""
import nodji as nd
import pandas as pd

from loguru import logger


def make_database_folder(func):
    def wrapper(self, *args, **kwargs):
        if not nd.exists_path(nd.Paths.DATABASE):
            nd.make_directory(nd.Paths.DATABASE)
        return func(self, *args, **kwargs)

    return wrapper


class DataFrameDataBase:

    def __init__(self, name: str):
        self.name = name
        self._df = pd.DataFrame()

    @property
    def exists(self):
        raise NotImplementedError(f"{self.__class__.__name__}.exists")

    @property
    def path(self):
        raise NotImplementedError(f"{self.__class__.__name__}.path")

    def load(self):
        raise NotImplementedError(f"{self.__class__.__name__}.load")

    @make_database_folder
    def save(self, dataframe: pd.DataFrame):
        raise NotImplementedError(f"{self.__class__.__name__}.save")


class DataFrameData(DataFrameDataBase):
    """일반적인 데이터프레임

    아마 나중에 monthly dataframe을 추가하려고 이렇게 둔것일거다
    """

    @property
    def exists(self):
        return nd.exists_path(self.path)

    @property
    def path(self):
        return nd.Paths.DATABASE / f"{self.name}.{nd.consts.Extensions.DATAFRAME_DATA}"

    def load(self) -> pd.DataFrame:
        if nd.exists_path(self.path):
            return pd.read_pickle(self.path)
        else:
            return pd.DataFrame()

    def save(self, dataframe: pd.DataFrame):
        dataframe.to_pickle(self.path)
        logger.info(f"{self.name}'s dataframe saved at {self.path}")


class MonthlyDataFrameData(DataFrameDataBase):
    """월별 데이터프레임

    시계열 데이터가 길어질 경우 저장하고 읽어오는데 시간이 많이 소비된다.
    그래서 월별로 나누어 시계열데이터를 저장할 수 있도록 하였다.
    """

