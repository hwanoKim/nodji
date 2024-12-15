from typing import TYPE_CHECKING, cast

import pandas as pd

import nodji as nd
from .price_collector_base import AsssetPriceCollectorBase
from ...converters.price_converters.coin_price_converter import CoinPriceConverter

if TYPE_CHECKING:
    from ...price_datas.coin_price_data import CoinPriceData
    from ....core.ntime import NTime


class CoinPriceCollector(AsssetPriceCollectorBase):
    """가격 데이터를 수집하는 클래스"""
    _price_data: 'CoinPriceData'

    def __init__(self, price_data: 'CoinPriceData'):
        super().__init__(price_data)
        self._ub = nd.external_apis.Upbit()

    @property
    def _conv(self):
        return CoinPriceConverter(self._price_data)

    def get_from_upbit(self, start_time: 'NTime', end_time: 'NTime'):
        """upbit에서 가격 데이터를 가져온다."""
        while True:
            new_data = self._ub.get_minute_candles(self._price_data._coin.ticker, end_time)
            new_df: pd.DataFrame = self._conv.api_to_dataframe(new_data)

            if new_df.empty:
                break

            self._data += new_df

            if start_time and start_time >= self._data.start_time:
                self._data.start_time = start_time
                break

            end_time = nd.NTime(new_df.index[0])


