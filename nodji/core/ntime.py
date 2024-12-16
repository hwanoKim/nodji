"""datetime 을 쓰기 편하도록 wrapping한 클래스"""
from datetime import datetime, timedelta
from typing import Union

import pandas as pd
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
        else:
            raise NotImplementedError(other, type(other))

    def __ge__(self, other):
        if isinstance(other, NTime):
            return self._time >= other._time
        else:
            raise NotImplementedError(other, type(other))

    def __lt__(self, other):
        if isinstance(other, NTime):
            return self._time < other._time
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
    def mon(self):
        return self._time.month

    @mon.setter
    def mon(self, value):
        while value > 12:
            value -= 12
            self._time = self._time.replace(year=self._time.year + 1)
        self._time = self._time.replace(month=value)

    @property
    def sec(self):
        return self._time.second

    @sec.setter
    def sec(self, value):
        minutes_to_add = value // 60
        value = value % 60
        self._time = self._time.replace(second=value)
        if minutes_to_add > 0:
            self._time += timedelta(minutes=minutes_to_add)

    @property
    def min(self):
        return self._time.minute

    @min.setter
    def min(self, value):
        hours_to_add = value // 60
        value = value % 60
        self._time = self._time.replace(minute=value)
        if hours_to_add > 0:
            self._time += timedelta(hours=hours_to_add)

    def to_utc(self):
        self.time_zone = nd.TimeZone.UTC
        return NTime(self._time.astimezone(self.time_zone.value), self.time_zone)

    def to_string(self):
        return self._time.strftime("%Y-%m-%d %H:%M:%S")

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
                else:
                    raise NotImplementedError(time, type(time))
        elif isinstance(time, datetime):
            pass
        else:
            raise NotImplementedError(time, type(time))

        if time is not None:
            time = time.replace(tzinfo=time_zone.value)
        return time
