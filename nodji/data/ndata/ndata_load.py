from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING
from dateutil.rrule import rrule, MONTHLY

import pandas as pd
import calendar

import nodji as nd

if TYPE_CHECKING:
    from .ndata import NData
    from ...core.ntime import NTime


class NDataLoaderBase:
    def __init__(self, ndata: 'NData'):
        self._ndata = ndata
        self._name = ndata.name
        self._path = ndata.path
        self._df = ndata._df

    @classmethod
    def has_matching_file(cls, name: str) -> bool:
        """해당 이름의 파일이 존재하는지 확인

        설명:
            각 loader에 맞는 파일이 존재하는지 확인한다.
                예를 들어 GeneralNDataLoader는 하나짜리 파일이 필요하다
                TimeSeriesNDataLoader는 Month별로 파일이 필요하기 때문에
                특정 이름의 폴더가 필요하다. 이런식으로 각각의 loader에 맞는
                파일이 존재하는지 확인하는 함수이다.

            exist로 시작하는거 보다
                has_matching_file로 시작하는게 더 좋은 이름이라고 한다.
                더 파이썬 스러운 이름이라고 해서 이렇게 지었다.
        """
        raise NotImplementedError("has_matching_file method must be implemented in DataFrameDataSaverBase")

    @classmethod
    def get_all_data_names(cls) -> list[str]:
        """load 할 수 있는 모든 데이터 이름을 반환"""
        raise NotImplementedError("get_all_data_names method must be implemented in DataFrameDataSaverBase")

    def load(self, start_time: 'NTime', end_time: 'NTime') -> pd.DataFrame:
        """데이터를 로드한다.

        설명:
            NData의 내부 형식인 pd.DataFrame을 반환한다
        """
        raise NotImplementedError("save method must be implemented in DataFrameDataSaverBase")


class NDataLoader(NDataLoaderBase):

    @classmethod
    def has_matching_file(cls, name: str) -> bool:
        return nd.exists_path(nd.Paths.DATABASE / f"{name}.df")

    @classmethod
    def get_all_data_names(cls) -> list[str]:
        return [file.split('.')[0]
                for file in nd.get_files_from_directory(nd.Paths.DATABASE,
                                                        ext=nd.consts.Extensions.DATAFRAME)]

    @property
    def _file_path(self):
        return nd.Paths.DATABASE / f"{self._name}.df"

    def load(self, start_time: 'NTime', end_time: 'NTime') -> pd.DataFrame:
        """파일에서 데이터를 불러온다.

        파일의 형식은 무조건 pickle로 저장되어 있어야 한다.
        """
        assert nd.exists_path(self._file_path), f"file not found: {self._file_path}"
        return pd.read_pickle(str(self._file_path))


class NTimeSeriesDataLoader(NDataLoaderBase):

    @classmethod
    def has_matching_file(cls, name: str) -> bool:
        return nd.exists_path(nd.Paths.DATABASE / name)

    @classmethod
    def get_all_data_names(cls) -> list[str]:
        return nd.get_folders_from_directory(nd.Paths.DATABASE)

    def load(self, start_time: 'NTime', end_time: 'NTime') -> pd.DataFrame:
        files = self._get_all_dataframe_files_from_folder()
        if not files:
            return pd.DataFrame()

        end_time, start_time = self._get_start_time_and_end_time(start_time, end_time, files)

        self._df = pd.DataFrame()

        for date in rrule(MONTHLY, dtstart=start_time.replace(day=1), until=end_time.replace(day=30)):
            file_path = self._get_monthly_file_path(date.year, date.month)
            if file_path in files:
                if self._df.empty:
                    self._df = nd.load_dataframe(file_path)
                else:
                    new_df = nd.load_dataframe(file_path)
                    self._df = pd.concat([self._df, new_df])

        self._df.sort_values(by='date', inplace=True)
        self._df = self._df[start_time <= self._df.index]
        self._df = self._df[self._df.index < end_time]
        return self._df

    def _get_start_time_and_end_time(self, start_time: 'NTime', end_time: 'NTime', files):
        if start_time.is_none:
            start_time = datetime.strptime(files[0].stem.split('.')[0][-6:], '%Y%m')
        else:
            start_time = start_time.to_datetime()
        if end_time.is_none:
            end_time = datetime.strptime(files[-1].stem.split('.')[0][-6:], '%Y%m')
            last_day = calendar.monthrange(end_time.year, end_time.month)[1]
            end_time = end_time.replace(day=last_day,
                                        hour=23,
                                        minute=59,
                                        second=59)
        else:
            end_time = end_time.to_datetime()

        if start_time.tzinfo is None:
            start_time = pd.Timestamp(start_time).tz_localize('Asia/Seoul')
        else:
            start_time = pd.Timestamp(start_time).tz_convert('Asia/Seoul')
        if end_time.tzinfo is None:
            end_time = pd.Timestamp(end_time).tz_localize('Asia/Seoul')
        else:
            end_time = pd.Timestamp(end_time).tz_convert('Asia/Seoul')
        return end_time, start_time

    def _get_monthly_file_path(self, year, month):
        file_name = self._name + '_' + str(year) + str(month).zfill(2)
        return nd.Paths.DATABASE / self._name / f"{file_name}.{nd.consts.Extensions.DATAFRAME}"

    def _get_all_dataframe_files_from_folder(self) -> list[Path]:
        folder_dir = nd.Paths.DATABASE / self._name
        if not nd.exists_path(folder_dir):
            return []
        return nd.get_files_from_directory(folder_dir)
