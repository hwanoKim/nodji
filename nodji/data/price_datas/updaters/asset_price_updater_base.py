import nodji as nd

from typing import TYPE_CHECKING
from loguru import logger

if TYPE_CHECKING:
    from nodji.data.price_datas.asset_price_data_base import AssetPriceDataBase


class AssetPriceDataUpdaterBase:
    """어셋의 가격 데이터를 업데이트한다.

    설명:
        업데이트의 의미는 다음과 같다.
            1. 기존 가격 데이터가 없을때:
                가격 데이터를 만든다. 가장 최신의 정보부터 과거로 쭉 업데이트 한다.

            2. 기존 정보가 있을때:
                a. 기존의 마지막 데이터부터 가장 최신의 데이터까지 채워준다.
                b. 가장 처음 시간의 가격에서 더 이전의 가격의 데이터가 있는지 확인하여 업데이트를 한다.
                c. 기존의 데이터에서 처음부터 마지막의 중간에 빈 시간의 부분을 한번씩 업데이트 해준다.
                    ex) 코인이라면 분단위 정보가 저장되어야 하는데 중간에 분단위로 빈 시간이 있다면 그것을 채워준다.
    """

    def __init__(self, price_data: 'AssetPriceDataBase'):
        self._price_data = price_data

    def __call__(self, start_time=None, end_time=None):
        self._start_time = nd.NTime(start_time)
        self._end_time = nd.NTime(end_time)
        self._validate_times()
        self._update()
        self._price_data.save()

    @property
    def _conv(self):
        raise NotImplementedError("converter property must be implemented in PriceUpdaterBase")

    def _update_origin_dataframe_from_time_range(self, start_time, end_time):
        """collector를 이용하여 상황에 맞게 값을 가져온다."""
        raise NotImplementedError("get_data_from_time_range method must be implemented in PriceUpdaterBase")

    def _update(self):
        """어셋의 가격 업데이트를 진행한다.

        설명:
            어셋의 가격를 처음 받을 때와
            기존에 데이터가 존재 할 때를 나누어 진행한다.
        """
        if self._price_data.exists:
            self._price_data.load(self._start_time, self._end_time)
        else:
            self._price_data.set_initial_data_columns()

        self._orig_df = self._price_data._df.copy()

        if self._orig_df.empty:
            self._update_price_if_empty()
        else:
            self._update_price_if_not_empty()
        self._price_data.set_dataframe(self._orig_df)

    def _update_price_if_empty(self):
        start_time, end_time = self._get_time_range_of_update_price_if_empty()
        self._update_origin_dataframe_from_time_range(start_time, end_time)

    def _get_time_range_of_update_price_if_empty(self):
        if self._end_time:
            end_time = self._end_time
        else:
            end_time = nd.NTime.get_current_time()
        return self._start_time, end_time

    def _update_price_if_not_empty(self):
        self._add_price_missing_time()
        self._add_price_after_original_dataframe()
        self._add_price_before_original_dataframe()

    def _validate_times(self):
        if not self._start_time.is_none and not self._end_time.is_none:
            assert self._start_time < self._end_time, "start_time must be less than end_time"

    def _add_price_after_original_dataframe(self):
        """기존 데이터의 마지막 시간부터 가장 최신의 시간까지 데이터를 추가한다."""
        if self._needs_update_after_original_dataframe():
            start_time, end_time = self._get_time_range_of_add_after_data()
            self._update_origin_dataframe_from_time_range(start_time, end_time)

    def _needs_update_before_original_ndataframe(self):
        """예전 데이터에서 첫 번째 날짜 이전으로 추가해야 하는지 확인한다."""
        if self._start_time:
            if self._start_time > self._orig_df.index[0]:
                return False
        return True

    def _needs_update_after_original_dataframe(self):
        """예전 데이터에서 마지막 날짜 이후로 추가해야 하는지 확인한다."""
        if self._end_time:
            if self._end_time < self._orig_df.index[-1]:
                return False
        return True

    def _get_time_range_of_add_before_data(self):
        end_time = nd.NTime(self._orig_df.index[0])
        if self._start_time:
            if end_time < self._start_time:
                start_time = end_time
            else:
                start_time = self._start_time
        else:
            start_time = nd.NTime(None)

        if self._end_time:
            if end_time > self._end_time:
                end_time = self._end_time

        return start_time, end_time

    def _get_time_range_of_add_after_data(self):
        start_time = nd.NTime(self._orig_df.index[-1])
        end_time = nd.NTime.get_current_time()

        if self._start_time:
            if start_time:
                if start_time < self._start_time:
                    start_time = self._start_time
            else:
                start_time = self._start_time

        if self._end_time:
            if end_time > self._end_time:
                end_time = self._end_time

        return start_time, end_time

    def _add_price_missing_time(self):
        missing_time_ranges = nd.find_missing_time_ranges_of_dataframe(self._orig_df)
        for start_time, end_time in missing_time_ranges:
            self._update_origin_dataframe_from_time_range(start_time, end_time)

    def _add_price_before_original_dataframe(self):
        if self._needs_update_before_original_ndataframe():
            start_time, end_time = self._get_time_range_of_add_before_data()
            print(start_time, end_time)
            self._update_origin_dataframe_from_time_range(start_time, end_time)
