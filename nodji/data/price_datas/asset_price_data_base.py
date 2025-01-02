from typing import TYPE_CHECKING

import pandas as pd

from .updaters.asset_price_updater_base import AssetPriceDataUpdaterBase
from ..ndata.ndata import NData

if TYPE_CHECKING:
    from ...assets.asset_base import TickerAssetBase


class AssetPriceDataBase(NData):
    update: 'AssetPriceDataUpdaterBase'

    def __init__(self, name: str):
        super().__init__(name)
        self._set_updater()

    def set_initial_data_columns(self):
        """PriceTypeBase 서브 클래스에서 구현한다"""
        raise NotImplementedError("make_empty_data method must be implemented in PriceTypeBase")

    def _set_updater(self):
        raise NotImplementedError("set_updater method must be implemented in AssetPriceDataBase")


class TickerPriceDataBase(AssetPriceDataBase):

    def __init__(self, asset: 'TickerAssetBase'):
        self._asset = asset
        super().__init__(asset.ticker)


class OHLCVData(TickerPriceDataBase):
    """OHLCV 데이터의 base class"""

    def set_initial_data_columns(self) -> pd.DataFrame:
        """빈 ohlcv dataframe 데이터를 만든다.

        이미 데이터가 있으면 안된다.

        Notes:
            columns:
                Open: 시가
                High: 고가
                Low: 저가
                Close: 종가
                Volume: 거래량
                TradePrice: 거래금액
        """
        assert self.is_empty, "data must be empty"
        self._df = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume', 'TradePrice'])
        return self._df


class MinutePriceData(TickerPriceDataBase):
    pass
