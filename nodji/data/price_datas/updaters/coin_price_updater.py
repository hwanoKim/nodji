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
    _price_data: 'CoinPriceData'

    def __init__(self, price_data: 'CoinPriceData'):
        super().__init__(price_data)
        self._ub = nd.external_apis.Upbit()

    @property
    def _conv(self):
        return CoinPriceConverter(self._price_data)

    def _update_dataframe_from_time_range(self, old_dataframe: pd.DataFrame,
                                          start_time: nd.NTime,
                                          end_time: nd.NTime) -> tuple[pd.DataFrame, bool]:
        """collector를 이용하여 상황에 맞게 값을 가져온다.

        설명:
            end_time을 copy를 하는 이유
                이 함수의 가장 아랫 줄에서 바깥쪽에서 end_time 변수에 새로운 값을 할당해 버려서
                외부의 end_time이 변하는 것을 막기 위해 copy를 한다.

            new_df의 row가 1개일때 멈추는 이유:
                get_minute_candles 함수는 특정 시간(end_time)을 넣으면 그 시간을 포함한 데이터를 반환한다.
                젤 아래에서 end_time = nd.NTime(new_df.index[0]) 이렇게 새로운 end_time을 할당하는데
                그 end_time이 포함된 딱 한줄짜리 데이터가 나온다는 뜻은 그 시간 이후로는 데이터가 없다는 뜻이다.
        """
        end_time = end_time.copy()

        while True:
            new_data = self._ub.get_minute_candles(self._price_data._asset.ticker, end_time)
            new_df = self._conv.api_to_dataframe(new_data)
            logger.info(f"{end_time} - {self._price_data._asset.ticker}")

            if new_df.empty or new_df.shape[0] == 1:
                self._stop_update = True
                break

            if old_dataframe.empty:
                old_dataframe = new_df
            else:
                stop = False

                if start_time and start_time >= new_df.index[0]:
                    new_df = new_df[new_df.index >= start_time.to_pandas_timestamp()]
                    stop = True
                old_dataframe = pd.concat([new_df, old_dataframe]).sort_index()
                old_dataframe = old_dataframe[~old_dataframe.index.duplicated(keep="first")]

                if stop:
                    break

            end_time = nd.NTime(new_df.index[0])

        return old_dataframe
