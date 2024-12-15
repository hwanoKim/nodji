from typing import TYPE_CHECKING

import nodji as nd
from ..ndata.ndata import NData

if TYPE_CHECKING:
    from ...assets.asset_base import AssetBase, TickerAssetBase


class AssetPriceDataBase(NData):

    def __init__(self, asset: 'AssetBase'):
        super().__init__('price')
        self._asset = asset

    @property
    def update(self):
        """가격 정보를 업데이트 한다."""
        raise NotImplementedError("update method must be implemented in PriceDataBase")

    def _set_initial_data_columns(self):
        """PriceTypeBase 서브 클래스에서 구현한다"""
        raise NotImplementedError("make_empty_data method must be implemented in PriceTypeBase")


class TickerPriceDataBase(AssetPriceDataBase):
    _asset: 'TickerAssetBase'

    def __init__(self, asset: 'TickerAssetBase'):
        super().__init__(asset)
        self._data = nd.DataFrameData(self._asset.ticker)


class PriceTypeBase(TickerPriceDataBase):
    """가격의 형식 base class"""


class OHLCVData(PriceTypeBase):

    def _set_initial_data_columns(self):
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
        assert not self._data.exists_file, f"{self._data.name} data already exists"
        self._data.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'TradePrice']


class TimeTypeBase(TickerPriceDataBase):
    """시간의 형식 base class"""
    pass


class MinutePriceData(TimeTypeBase):
    pass
