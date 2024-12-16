from typing import TYPE_CHECKING

from ..ndata.ndata import NData

if TYPE_CHECKING:
    from ...assets.asset_base import TickerAssetBase


class AssetPriceDataBase(NData):

    def __init__(self, name: str):
        super().__init__(name)

    @property
    def update(self):
        """가격 정보를 업데이트 한다."""
        raise NotImplementedError("update method must be implemented in PriceDataBase")

    def _set_initial_data_columns(self):
        """PriceTypeBase 서브 클래스에서 구현한다"""
        raise NotImplementedError("make_empty_data method must be implemented in PriceTypeBase")


class TickerPriceDataBase(AssetPriceDataBase):

    def __init__(self, asset: 'TickerAssetBase'):
        self._asset = asset
        super().__init__(asset.ticker)


class OHLCVData(TickerPriceDataBase):
    """OHLCV 데이터의 base class"""

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
        assert not self.exists, f"{self.name} data already exists"
        assert self.is_empty, "data must be empty"
        self._ndf.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'TradePrice']


class MinutePriceData(TickerPriceDataBase):
    pass
