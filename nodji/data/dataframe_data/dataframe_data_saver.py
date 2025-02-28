from typing import TYPE_CHECKING
from dateutil.rrule import rrule, MONTHLY

import pandas as pd
import calendar

import nodji as nd

if TYPE_CHECKING:
    from .datafame_data import DataFrameData


def make_database_folder(func):
    def wrapper(self, *args, **kwargs):
        if not nd.exists_path(nd.Paths.DATABASE):
            nd.make_directory(nd.Paths.DATABASE)
        return func(self, *args, **kwargs)

    return wrapper


class DataFrameDataSaverBase:
    def __init__(self, data: 'DataFrameData'):
        self._data = data
        self._name = data.name
        self._df = data._df
        self._path = data.path

    @classmethod
    def is_match(cls, dataframe: pd.DataFrame) -> bool:
        raise NotImplementedError("is_match method must be implemented in DataFrameDataSaverBase")

    @make_database_folder
    def save(self):
        raise NotImplementedError("save method must be implemented in DataFrameDataSaverBase")


class DatetimeIndexSaver(DataFrameDataSaverBase):
    @classmethod
    def is_match(cls, dataframe: pd.DataFrame) -> bool:
        return isinstance(dataframe.index, pd.DatetimeIndex)

    @make_database_folder
    def save(self):
        if not nd.exists_path(self._path):
            nd.make_directory(self._path)
        if self._df.empty:
            return

        start_date = self._df.index[0]
        end_date = self._df.index[-1]
        last_day = calendar.monthrange(end_date.year, end_date.month)[1]

        for date in rrule(MONTHLY, dtstart=start_date.replace(day=1), until=end_date.replace(day=last_day)):
            new_df = self._df[(self._df.index.year == date.year) &
                              (self._df.index.month == date.month)]

            file_path = self._get_monthly_file_path(date.year, date.month)
            if nd.exists_path(file_path):
                old_df = nd.load_dataframe_file(file_path)
                new_df = nd.merge_dataframe_by_date(new_df, old_df)
            nd.save_dataframe_file(new_df, file_path)

    def _get_monthly_file_path(self, year, month):
        file_name = self._name + '_' + str(year) + str(month).zfill(2)
        return self._path / f"{file_name}.{nd.consts.Extensions.DATAFRAME_DATA}"


class NonDatetimeIndexSaver(DataFrameDataSaverBase):
    @classmethod
    def is_match(cls, dataframe: pd.DataFrame) -> bool:
        return not isinstance(dataframe.index, pd.DatetimeIndex)

    @make_database_folder
    def save(self):
        self._df.to_pickle(self._path)

