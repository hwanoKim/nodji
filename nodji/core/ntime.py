"""datetime 을 쓰기 편하도록 wrapping한 클래스"""
from datetime import datetime, timedelta
from typing import Union

import pandas as pd
from dateutil.relativedelta import relativedelta
from pandas import Timestamp

import nodji as nd


class NTime:
    """시간 관리를 쉽게 하려고 내가 이해하기 쉬운 방법으로 WRAPPING 하였다.

    Notes:
        내부에서는 datetime을 사용하고 있다.
        pd.Timestamp를 datetime으로 변환하여 사용한다.
    """

    def __init__(self, time: Union[datetime, pd.Timestamp, type(None)], time_zone: nd.TimeZone = nd.TimeZone.SEOUL):
        time = self._convert_time_value(time, time_zone)
        self._time = time
        self.time_zone = time_zone

    def __bool__(self):
        return not self.is_none

    def __repr__(self):
        if self.is_none:
            return 'None'
        else:
            return self._time.strftime("%Y/%m/%d %H:%M:%S")

    def __gt__(self, other):
        if isinstance(other, NTime):
            return self._time > other._time
        elif isinstance(other, Timestamp):
            return self._time > NTime(other)
        elif isinstance(other, datetime):
            return self._time > other
        else:
            raise NotImplementedError(other, type(other))

    def __ge__(self, other):
        if isinstance(other, NTime):
            return self._time >= other._time
        elif isinstance(other, Timestamp):
            return self._time >= other
        else:
            raise NotImplementedError(other, type(other))

    def __lt__(self, other):
        if isinstance(other, NTime):
            return self._time < other._time
        elif isinstance(other, Timestamp):
            return self._time < NTime(other)
        elif isinstance(other, datetime):
            return self._time < other
        else:
            raise NotImplementedError(other, type(other))

    def __le__(self, other):
        if isinstance(other, NTime):
            return self._time <= other._time
        else:
            raise NotImplementedError(other, type(other))

    def __eq__(self, other):
        if isinstance(other, NTime):
            return self._time == other._time
        else:
            raise NotImplementedError(other, type(other))

    @property
    def is_none(self):
        return self._time is None

    @classmethod
    def get_current_time(cls):
        return cls(datetime.now(tz=nd.TimeZone.SEOUL.value))

    @property
    def year(self):
        return self._time.year

    @year.setter
    def year(self, value):
        self._time = self._time.replace(year=value)

    @property
    def hour(self):
        return self._time.hour

    @hour.setter
    def hour(self, value):
        days_to_add = value // 24
        value = value % 24
        self._time = self._time.replace(hour=value)
        if days_to_add > 0:
            self._time += timedelta(days=days_to_add)

    @property
    def mon(self) -> int:
        return self._time.month

    @mon.setter
    def mon(self, value):
        month_difference = value - self._time.month

        # relativedelta를 사용해 월 차이를 계산
        self._time += relativedelta(months=month_difference)

        # 월 변경 후 현재 날짜가 유효하지 않다면, 해당 월의 마지막 날로 설정
        while True:
            try:
                self._time = self._time.replace(day=self._time.day)
                break
            except ValueError:
                self._time = self._time.replace(day=self._time.day - 1)

    @property
    def day(self) -> int:
        return self._time.day

    @day.setter
    def day(self, value):
        day_difference = value - self._time.day
        self._time += timedelta(days=day_difference)

    @property
    def sec(self) -> int:
        return self._time.second

    @sec.setter
    def sec(self, value):
        seconds_difference = value - self._time.second
        self._time += timedelta(seconds=seconds_difference)

    @property
    def min(self) -> int:
        return self._time.minute

    @min.setter
    def min(self, value):
        minutes_difference = value - self._time.minute
        self._time += timedelta(minutes=minutes_difference)

    def copy(self):
        return NTime(self._time, self.time_zone)

    def to_utc(self):
        self.time_zone = nd.TimeZone.UTC
        return NTime(self._time.astimezone(self.time_zone.value), self.time_zone)

    def to_string(self):
        return self._time.strftime("%Y-%m-%d %H:%M:%S")

    def to_datetime(self):
        return self._time

    def to_pandas_timestamp(self) -> Timestamp:
        """
        현재 NTime 객체를 pandas.Timestamp로 변환합니다.

        Returns:
            pandas.Timestamp: 변환된 pandas.Timestamp 객체.
        """
        if self.is_none:
            raise ValueError("Cannot convert None to pandas.Timestamp")
        return pd.Timestamp(self._time)

    def get_last_day_of_month(self) -> int:
        next_month = self._time.replace(day=28) + timedelta(days=4)
        last_day = next_month.replace(day=1) - timedelta(days=1)
        return last_day.day

    def _convert_time_value(self, time, time_zone):
        """

        Notes:
            None:
                time이 None인것도 허용하고 있다.
                is_none으로 확인할 수 있다.

            pd.Timestamp:
                datetime으로 변환하여 사용한다.
        """
        if time is None:
            pass
        elif isinstance(time, pd.Timestamp):
            time = time.to_pydatetime()
        elif isinstance(time, str):
            if ' ' in time:
                raise NotImplementedError(time, type(time))
            else:
                if len(time) == 8:
                    time = datetime.strptime(time, '%Y%m%d')
                elif len(time) == 6:
                    if int(time[:2]) < 50:
                        time = '20' + time
                    else:
                        time = '19' + time
                    time = datetime.strptime(time, '%Y%m%d')
                else:
                    raise NotImplementedError(time, type(time))
        elif isinstance(time, datetime):
            pass
        elif isinstance(time, NTime):
            time = time._time
        else:
            raise NotImplementedError(time, type(time))

        if time is not None:
            time = time.replace(tzinfo=time_zone.value)
        return time
