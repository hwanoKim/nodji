from typing import Optional

import nodji as nd
import pandas as pd

from loguru import logger


class DataFrameDataBase:

    def __init__(self, name: str):
        self.name = name

    @property
    def exists(self):
        raise NotImplementedError(f"{self.__class__.__name__}.exists")

    @property
    def path(self):
        raise NotImplementedError(f"{self.__class__.__name__}.path")

    def load(self):
        raise NotImplementedError(f"{self.__class__.__name__}.load")

    def save(self, dataframe: pd.DataFrame):
        if not nd.exists_path(nd.constants.DATABASE_PATH):
            nd.make_directory(nd.constants.DATABASE_PATH)
        self._save(dataframe)

    def _save(self, dataframe: pd.DataFrame):
        raise NotImplementedError(f"{self.__class__.__name__}.save")


class DataFrameData(DataFrameDataBase):
    """일반적인 데이터프레임"""

    @property
    def exists(self):
        return nd.exists_path(self.path)

    @property
    def path(self):
        return nd.constants.DATABASE_PATH + self.name + '.' + nd.constants.DATAFRAME_EXT

    def load(self) -> pd.DataFrame:
        if nd.exists_path(self.path):
            return pd.read_pickle(self.path)
        else:
            return pd.DataFrame()

    def _save(self, dataframe: pd.DataFrame):
        dataframe.to_pickle(self.path)
        logger.info(f"{self.name}'s dataframe saved at {self.path}")
