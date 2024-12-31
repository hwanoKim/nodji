from typing import TYPE_CHECKING

import pandas as pd

import nodji as nd
from .asset_price_updater_base import AssetPriceDataUpdaterBase
from ...converters.price_converters.coin_price_converter import CoinPriceConverter
from loguru import logger

if TYPE_CHECKING:
    from ..coin_price_data import CoinPriceData
    from ....core.ntime import NTime


class CoinPriceUpdater(AssetPriceDataUpdaterBase):
    """코인의 가격 정보를 업데이트한다.

    설명:
        코인가격의 업데이트의 의미는 다음과 같다.
            1. 기존 가격정보가 없을때:
                가격 정보를 만든다. 가장 최신의 가격정보부터 과거로 쭉 업데이트 한다.

            2. 가격정보가 있을때:
                a. 가장 최신의 가격에서 기존의 마지막 데이터까지 채워준다.
                b. 가장 처음 시간의 가격에서 더 이전의 가격의 데이터가 있는지 확인하여 업데이트를 한다.
                c. 기존의 데이터에서 처음부터 마지막의 중간에 빈 시간의 부분을 한번씩 업데이트 해준다.
                    코인은 분단위 정보가 저장되어야 하는데 중간에 분단위로 빈 시간이 있다면 그것을 채워준다.
    """
    _price_data: 'CoinPriceData'

    def __init__(self, price_data: 'CoinPriceData'):
        super().__init__(price_data)
        self._ub = nd.external_apis.Upbit()

    @property
    def _conv(self):
        return CoinPriceConverter(self._price_data)

    def _update_origin_dataframe_from_time_range(self, start_time: nd.NTime, end_time: nd.NTime):
        while True:
            new_data = self._ub.get_minute_candles(self._price_data._asset.ticker, end_time)
            new_df = self._conv.api_to_dataframe(new_data)
            logger.info(f"{end_time} - {self._price_data._asset.ticker}")

            if new_df.empty:
                break

            if self._orig_df.empty:
                self._orig_df = new_df
            else:
                stop = False

                if start_time and start_time >= new_df.index[0]:
                    new_df = new_df[new_df.index >= start_time.to_pandas_timestamp()]
                    stop = True
                self._orig_df = pd.concat([new_df, self._orig_df]).sort_index()
                self._orig_df = self._orig_df[~self._orig_df.index.duplicated(keep="first")]

                if stop:
                    break

            end_time = nd.NTime(new_df.index[0])
