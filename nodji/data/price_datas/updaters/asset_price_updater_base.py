from nodji.data.price_datas.asset_price_data_base import AssetPriceDataBase
import nodji as nd


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
        self._data: nd.DataFrameData = price_data._data

    def __call__(self, start_time=None, end_time=None):
        self._start_time = nd.NTime(start_time)
        self._end_time = nd.NTime(end_time)
        self._validate_times()
        self._update()
        self._data.save()

    @property
    def _coll(self):
        raise NotImplementedError("coll property must be implemented in PriceUpdaterBase")

    def _update_data_from_time_range(self, start_time, end_time):
        """collector를 이용하여 상황에 맞게 값을 가져온다."""
        raise NotImplementedError("get_data_from_time_range method must be implemented in PriceUpdaterBase")

    def _update(self):
        if not self._data.exists_file:
            self._price_data._set_initial_data_columns()
        self._orig_data = self._data.copy()

        self._add_price_after_data()
        # self._add_price_before_data(old_end_time)
        # self._add_price_missing_time(old_start_time, old_end_time)

    def _validate_times(self):
        if not self._start_time.is_none and not self._end_time.is_none:
            assert self._start_time < self._end_time, "start_time must be less than end_time"

    def _add_price_after_data(self):
        """기존 데이터의 마지막 시간부터 가장 최신의 시간까지 데이터를 추가한다."""
        if self._needs_update_after_data():
            start_time, end_time = self._get_time_range_of_add_after_data()
            self._update_data_from_time_range(start_time, end_time)

    def _needs_update_after_data(self):
        """데이터를 추가해야 하는지 확인한다."""
        if self._end_time:
            if self._orig_data.exists_data:
                if self._end_time < self._orig_data.end_time:
                    return False
        return True

    def _get_time_range_of_add_after_data(self):
        start_time = self._orig_data.end_time
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

    def _add_price_missing_time(self, old_start_time, old_end_time):
        data = self._data[old_start_time:old_end_time]
        for start_time, end_time in data.missing_times:
            self._data += self._coll.get_from_upbit(start_time, end_time)

    def _add_price_before_data(self, old_start_time):
        start_time = self._get_time_range_of_add_after_data(old_end_time)
        end_time = self._get_end_time_of_add_after_data(old_end_time)
        self._data += self._coll.get_from_upbit(start_time, end_time)
