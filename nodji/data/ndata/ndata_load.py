from typing import TYPE_CHECKING
from dateutil.rrule import rrule, MONTHLY

import pandas as pd
import calendar

import nodji as nd

if TYPE_CHECKING:
    from .ndata import NData


class NDataLoaderBase:
    def __init__(self, ndata: 'NData'):
        self._ndata = ndata
        self._name = ndata.name
        self._ndf = ndata._ndf

    @classmethod
    def has_matching_file(cls, name: str) -> bool:
        """해당 이름의 파일이 존재하는지 확인

        설명:
            각 loader에 맞는 파일이 존재하는지 확인한다.
                예를 들어 GeneralNDataLoader는 하나짜리 파일이 필요하다
                TimeSeriesNDataLoader는 Month별로 파일이 필요하기 때문에
                특정 이름의 폴더가 필요하다. 이런식으로 각각의 loader에 맞는
                파일이 존재하는지 확인하는 함수이다.
        """
        raise NotImplementedError("has_matching_file method must be implemented in DataFrameDataSaverBase")

    @classmethod
    def get_all_data_names(cls) -> list[str]:
        """load 할 수 있는 모든 데이터 이름을 반환"""
        raise NotImplementedError("get_all_data_names method must be implemented in DataFrameDataSaverBase")

    @classmethod
    def is_match(cls, dataframe: pd.DataFrame) -> bool:
        raise NotImplementedError("is_match method must be implemented in DataFrameDataSaverBase")

    def load(self) -> 'nd.NDataFrame':
        """데이터를 로드한다.

        설명:
            NData의 내부 형식인 pd.DataFrame을 반환한다
        """
        raise NotImplementedError("save method must be implemented in DataFrameDataSaverBase")


class GeneralNDataLoader(NDataLoaderBase):
    @classmethod
    def is_match(cls, dataframe: pd.DataFrame) -> bool:
        return not isinstance(dataframe.index, pd.DatetimeIndex)

    @classmethod
    def has_matching_file(cls, name: str) -> bool:
        return nd.exists_path(nd.Paths.DATABASE / f"{name}.df")

    @classmethod
    def get_all_data_names(cls) -> list[str]:
        return [file.split('.')[0]
                for file in nd.get_files_from_directory(nd.Paths.DATABASE,
                                                        ext=nd.consts.Extensions.NDATA)]

    @property
    def _file_path(self):
        return nd.Paths.DATABASE / f"{self._name}.df"

    def load(self) -> 'nd.NDataFrame':
        """파일에서 데이터를 불러온다.

        파일의 형식은 무조건 pickle로 저장되어 있어야 한다.
        """
        assert nd.exists_path(self._file_path), f"file not found: {self._file_path}"
        return nd.NDataFrame(pd.read_pickle(str(self._file_path)))


class TimeSeriesNDataLoader(NDataLoaderBase):
    @classmethod
    def is_match(cls, dataframe: pd.DataFrame) -> bool:
        return isinstance(dataframe.index, pd.DatetimeIndex)

    @classmethod
    def has_matching_file(cls, name: str) -> bool:
        return nd.exists_path(nd.Paths.DATABASE / name)

    @classmethod
    def get_all_data_names(cls) -> list[str]:
        return nd.get_folders_from_directory(nd.Paths.DATABASE)

    def load(self) -> 'nd.NDataFrame':
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
        return self._path / f"{file_name}.{nd.consts.Extensions.NDATA}"
