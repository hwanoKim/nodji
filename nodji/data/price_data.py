from typing import TYPE_CHECKING
from ..collector.coin_collector import CoinPriceCollector
import nodji as nd

if TYPE_CHECKING:
    from ..assets.asset_base import AssetBase, TickerAssetBase


class PriceDataBase:

    def __init__(self, asset: 'AssetBase'):
        self._asset = asset
        self._data = None

    @property
    def start_time(self):
        return

    @property
    def end_time(self):
        return

    @property
    def _price_coll(self):
        raise NotImplementedError("price_coll property must be implemented in PriceDataBase")

    def update(self):
        raise NotImplementedError("update method must be implemented in PriceDataBase")

    def _load_price(self):
        raise NotImplementedError("load_price method must be implemented in PriceDataBase")


class TickerPriceDataBase(PriceDataBase):
    _asset: 'TickerAssetBase'

    def __init__(self, asset: TickerAssetBase):
        super().__init__(asset)
        self._data = nd.DataFrameData(self._asset.ticker)


class OHLCVData:
    pass


class MinutePriceData:
    pass


class CoinPriceData(TickerPriceDataBase, MinutePriceData, OHLCVData):
    @property
    def _price_coll(self):
        return CoinPriceCollector(self)

    def update(self):
        pass

    def _load_price(self):
        pass
