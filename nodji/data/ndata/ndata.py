from pathlib import Path

import nodji as nd
import pandas as pd
from dateutil.rrule import rrule, MONTHLY
import calendar
from loguru import logger
from ...core.ntime import NTime
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.ntime import NTime


def make_database_folder(func):
    def wrapper(self, *args, **kwargs):
        if not nd.exists_path(nd.Paths.DATABASE):
            nd.make_directory(nd.Paths.DATABASE)
        return func(self, *args, **kwargs)

    return wrapper


class NDataBase:
    """데이터를 저장하고 불러오는 등 관리를 위한 클래스.

    설명:
        특징:
            데이터는 이름으로 구분한다.
            이름을 기반으로 저장하고 불러올 수 있다.
            내부에서는 pd.DataFrame을 기반으로 한다.

        저장 / 불러오기:
            이름을 기반으로 하여 저장 / 불러오기 기능을 포함하였다.
            이름으로한 경로가 자동으로 지정된다.

            이름을 기준으로 Data가 정의 되는데 Data의 instance를 생성해도
            자동으로 load하거나 하지는 않는다.
            instance만 생성하고 필요할때만 실제 데이터를 읽는다.

        확장자:
            결국 실제 저장은 최종적으로 DataFrame을 저장하기 때문에
            개별적 파일은 .df로 저장한다.
    """

    def __init__(self, name: str):
        self._name = name
        self._df = pd.DataFrame()

    def __repr__(self):
        return str(self._df)

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        raise NotImplementedError(f"path method must be implemented in {self.__class__.__name__}")

    @property
    def exists(self):
        """저장된 데이터가 존재하는가?

        설명:
            is_empty와 헷갈릴 수 있다.
                is_empty는 저장되어 있던 데이터가 존재할때
                비어있는지를 확인하는 것이다.
        """
        return nd.exists_path(self.path)

    @property
    def is_empty(self):
        return self._df.empty

    @property
    def cols(self) -> list[str]:
        """column의 이름을 리스트로 반환한다."""
        return self._df.columns

    @cols.setter
    def cols(self, value):
        """column의 이름을 설정한다."""
        self._df.columns = value

    def set_dataframe(self, dataframe: pd.DataFrame):
        assert isinstance(dataframe, pd.DataFrame), f"dataframe must be pd.DataFrame but {type(dataframe)}"
        self._df = dataframe
        return self


class NData(NDataBase):
    """데이터를 저장하고 불러오는 등 관리를 위한 클래스.

    설명:
        시간 단위의 개념
            또한 저장할 때 자동으로 너무 긴 시계열의 데이터를 분할 저장, 불러오기의 기능도 함께 한다.
            시계열 index를 가지는 데이터라면 시간 단위에 따라서 분할 한다.
            예를 들어 index가 분당인 데이터는 Monlty로 저장한다.
            index가 일단위 데이터는 Yearly로 저장한다.
    """

    @property
    def path(self):
        """현재의 데이터를 기반으로 저장할 경로를 반환한다."""
        return nd.Paths.DATABASE / f"{self._name}.df"

    def load(self) -> 'pd.DataFrame':
        """읽어온다. 없으면 빈 데이터프레임을 반환한다."""
        if not self.exists:
            return pd.DataFrame()
        return pd.read_pickle(str(self.path))

    def save(self):
        nd.save_dataframe(self._df, self.path)


class NTimeSeriesData(NDataBase):
    """index가 시계열인 데이터를 저장하는 클래스.

    설명:
        시간 단위의 개념
            또한 저장할 때 자동으로 너무 긴 시계열의 데이터를 분할 저장, 불러오기의 기능도 함께 한다.
            시계열 index를 가지는 데이터라면 시간 단위에 따라서 분할 한다.
            예를 들어 index가 분당인 데이터는 Monlty로 저장한다.
            index가 일단위 데이터는 Yearly로 저장한다.
    """

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
    def start_time(self) -> 'NTime':
        """현재 로드된 데이터의 시작 시간 반환"""
        assert not self._df.empty, f"{self._name} data is empty"
        return NTime(self._df.index.min())

    @property
    def end_time(self) -> 'NTime':
        """현재 로드된 데이터의 마지막 시간 반환"""
        assert not self._df.empty, f"{self._name} data is empty"
        return NTime(self._df.index.max())

    @property
    def total_start_time(self) -> 'NTime':
        """서버에 저장된 전체 데이터의 시작 시간 반환"""
        files = self._get_all_dataframe_file_paths_from_folder()
        if not files:
            return NTime(None)  # 데이터가 없으면 None 반환
        start_time = datetime.strptime(files[0].stem.split('.')[0][-6:], '%Y%m')
        return NTime(pd.Timestamp(start_time).tz_localize('Asia/Seoul'))

    @property
    def total_end_time(self) -> 'NTime':
        """서버에 저장된 전체 데이터의 마지막 시간 반환"""
        files = self._get_all_dataframe_file_paths_from_folder()
        if not files:
            return NTime(None)  # 데이터가 없으면 None 반환
        df = nd.load_dataframe(files[-1])
        return NTime(df.index[-1])

    @property
    def path(self):
        return nd.Paths.DATABASE / self.name

    def load(self, start_time: 'NTime', end_time: 'NTime') -> pd.DataFrame:
        """만약 해당하는 데이터가 없다면 빈 데이터프레임을 반환한다."""
        files = self._get_all_dataframe_file_paths_from_folder()
        if not files:
            return pd.DataFrame()

        end_time, start_time = self._get_start_time_and_end_time(start_time, end_time, files)

        self._df = pd.DataFrame()

        for date in rrule(MONTHLY,
                          dtstart=start_time.replace(day=1),
                          until=end_time.replace(day=calendar.monthrange(end_time.year, end_time.month)[1])):
            file_path = self._get_monthly_file_path(date.year, date.month)
            if not nd.exists_path(file_path):
                continue
            if file_path in files:
                if self._df.empty:
                    self._df = nd.load_dataframe(file_path)
                else:
                    new_df = nd.load_dataframe(file_path)
                    self._df = pd.concat([self._df, new_df])

        if not self._df.empty:
            self._df.sort_values(by='date', inplace=True)
            self._df = self._df[start_time <= self._df.index]
            self._df = self._df[self._df.index < end_time]
        return self._df

    @make_database_folder
    def save(self):
        if not nd.exists_path(self.path):
            nd.make_directory(self.path)
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
                old_df = nd.load_dataframe(file_path)
                new_df = nd.merge_dataframe_by_date(old_df, new_df)
            nd.save_dataframe(new_df, file_path)

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
        return self.path / f"{file_name}.{nd.consts.Extensions.DATAFRAME}"

    def _get_all_dataframe_file_paths_from_folder(self) -> list[Path]:
        folder_dir = nd.Paths.DATABASE / self._name
        if not nd.exists_path(folder_dir):
            return []
        return nd.get_files_from_directory(folder_dir)
