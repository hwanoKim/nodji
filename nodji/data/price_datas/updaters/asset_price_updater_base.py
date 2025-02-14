import pandas as pd

import nodji as nd

from typing import TYPE_CHECKING
from loguru import logger
from loguru import logger

if TYPE_CHECKING:
    from nodji.data.price_datas.asset_price_data_base import AssetPriceDataBase


class AssetPriceDataUpdaterBase:

    def __init__(self, price_data: 'AssetPriceDataBase'):
        self._price_data = price_data

    def __call__(self, start_time=None, end_time=None, backfill: bool = False):
        """어셋의 가격 데이터를 업데이트한다.

        설명:
            업데이트의 의미는 다음과 같다.
                1. 기존 가격 데이터가 없을때:
                    가격 데이터를 만든다.
                    가장 최신의 정보부터 과거로 쭉 업데이트 한다.

                2. 기존 정보가 있을때:
                    backfill is True:
                        세가지 파트로 나뉘어서 진행한다.
                        a. 마지막 데이터에서 가장 최신의 가격까지 업데이트 한다.
                        b. 기존 데이터의 가장 처음 데이터이전의 가격들을 업데이트 한다.
                        c. 기존 데이터에서 시간 단위별로 확인해서 빠진 부분이 있다면 다시 업데이트 한다.

                    backfill is False:
                        start_time의 날짜를 가장 마지막 데이터로 변경해준다.
                        기존의 마지막 데이터부터 가장 최신의 데이터까지 채워준다.
        """
        self._start_time = nd.NTime(start_time)
        self._end_time = nd.NTime(end_time)
        self._backfill = backfill
        self._set_valid_times()
        self._update()
        logger.info(f"update '{self._price_data.name}' price data")

    @property
    def _conv(self):
        raise NotImplementedError("converter property must be implemented in PriceUpdaterBase")

    def _update_dataframe_from_time_range(self, old_dataframe: pd.DataFrame,
                                          start_time: nd.NTime, end_time: nd.NTime) -> pd.DataFrame:
        """collector를 이용하여 상황에 맞게 값을 가져온다."""
        raise NotImplementedError("get_data_from_time_range method must be implemented in PriceUpdaterBase")

    def _update(self):
        """어셋의 가격 업데이트를 진행한다.

        설명:
            달별로 진행한다:
                데이터를 달별로 업데이트 하고 저장한다.
                몇년치 데이터를 계속해서 메모리에 저장하고 있으면
                api 호출이 가공 병합 등에서 메모리에 부하가 계속된다. 따라서
                각 달별로 진행하여 이러한 부하를 줄인다.

            설명:
                start_time, end_time:
                    각 달의 시작시간과 끝 시간을 지정해준다.
        """
        monthly_end_time = self._get_monthly_end_time()
        self._stop_update = False

        while True:
            monthly_start_time = self._get_monthly_start_time(monthly_end_time)
            df = self._update_dataframe(monthly_end_time, monthly_start_time)
            self._save_dataframe(df)
            monthly_end_time = self._get_end_time_of_previous_month(monthly_end_time)
            if self._stop_update:
                break

    def _save_dataframe(self, df):
        self._price_data.set_dataframe(df)
        self._price_data.save()

    def _update_dataframe(self, end_time, start_time):
        """기존의 데이터를 불러와서 업데이트 한다."""
        df = self._price_data.load(start_time, end_time)
        if df.empty:
            df = self._update_dataframe_from_time_range(self._price_data.set_initial_data_columns(),
                                                        start_time, end_time)
        else:
            df = self._update_price_if_not_empty(df, start_time, end_time)
        return df

    def _get_monthly_start_time(self, end_time):
        """달별 start_time을 반환한다."""
        start_time = self._convert_to_start_of_month(end_time)
        start_time = self._adjust_start_time(start_time)
        return start_time

    def _adjust_start_time(self, start_time):
        """self._start_time과 비교하여 start_time을 조정한다."""
        if self._start_time:
            if start_time <= self._start_time:
                start_time = self._start_time
                self._stop_update = True
        return start_time

    def _convert_to_start_of_month(self, end_time: nd.NTime) -> nd.NTime:
        """end_time을 복사해서 그 달의 첫번째 날로 시간을 바꿔준다."""
        start_time = end_time.copy()
        start_time.day = 1
        start_time.hour = 0
        start_time.min = 0
        start_time.sec = 0
        return start_time

    def _get_end_time_of_previous_month(self, end_time: nd.NTime) -> nd.NTime:
        """이전 달의 마지막 시간을 반환한다."""
        end_time.mon -= 1
        end_time.day = end_time.get_last_day_of_month()
        end_time.hour = 23
        end_time.min = 59
        end_time.sec = 59
        return end_time

    def _get_monthly_end_time(self) -> nd.NTime:
        if self._end_time.is_none:
            return nd.NTime.get_current_time()
        return self._end_time

    def _update_price_if_not_empty(self, old_dataframe: pd.DataFrame,
                                   start_time: nd.NTime, end_time: nd.NTime) -> pd.DataFrame:
        df = self._backfill_price_data(end_time, old_dataframe, start_time)
        return self._add_price_after_original_dataframe(df, start_time, end_time)

    def _backfill_price_data(self, end_time, old_dataframe, start_time):
        if self._backfill:
            df = self._add_price_missing_time(old_dataframe)
            df = self._add_price_before_original_dataframe(df, start_time, end_time)
            return df
        else:
            return old_dataframe

    def _set_valid_times(self):
        """update를 위해서 유효한 시간 설정을 해주는 함수"""
        if self._price_data.exists and not self._backfill:
            self._start_time = self._price_data.total_end_time

        if not self._start_time.is_none and not self._end_time.is_none:
            assert self._start_time < self._end_time, "start_time must be less than end_time"

    def _add_price_after_original_dataframe(self, old_dataframe: pd.DataFrame,
                                            start_time: nd.NTime, end_time: nd.NTime) -> pd.DataFrame:
        """기존 데이터의 마지막 시간부터 가장 최신의 시간까지 데이터를 추가한다."""
        if self._needs_update_after_original_dataframe(old_dataframe, end_time):
            start_time = self._get_start_time_of_add_after_data(old_dataframe, start_time)
            return self._update_dataframe_from_time_range(old_dataframe, start_time, end_time)
        return old_dataframe

    def _needs_update_before_original_dataframe(self, old_dataframe: pd.DataFrame, start_time: nd.NTime) -> bool:
        """예전 데이터에서 첫 번째 날짜 이전으로 추가해야 하는지 확인한다."""
        return start_time < old_dataframe.index[0]

    def _needs_update_after_original_dataframe(self, old_dataframe, end_time):
        return end_time > old_dataframe.index[-1]

    def _get_time_range_of_add_before_data(self, old_dataframe: pd.DataFrame, end_time: nd.NTime) -> nd.NTime:
        if end_time > old_dataframe.index[0]:
            return nd.NTime(old_dataframe.index[0])
        return end_time

    def _get_start_time_of_add_after_data(self, old_dataframe: pd.DataFrame, start_time: nd.NTime):
        if nd.NTime(old_dataframe.index[-1]) > start_time:
            start_time = nd.NTime(old_dataframe.index[-1])
        return start_time

    def _add_price_missing_time(self, old_dataframe: pd.DataFrame) -> pd.DataFrame:
        df = old_dataframe
        missing_time_ranges = nd.find_missing_time_ranges_of_dataframe(df)
        for start_time, end_time in missing_time_ranges:
            df = self._update_dataframe_from_time_range(df, start_time, end_time)
        return df

    def _add_price_before_original_dataframe(self, old_dataframe: pd.DataFrame,
                                             start_time: nd.NTime, end_time: nd.NTime) -> pd.DataFrame:
        if self._needs_update_before_original_dataframe(old_dataframe, start_time):
            end_time = self._get_time_range_of_add_before_data(old_dataframe, end_time)
            return self._update_dataframe_from_time_range(old_dataframe, start_time, end_time)
        return old_dataframe
