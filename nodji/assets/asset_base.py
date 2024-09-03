from dataclasses import dataclass
from ..data.price_datas.asset_price_data_base import AssetPriceDataBase


@dataclass
class AssetBase:
    @property
    def price(self):
        return AssetPriceDataBase(self)

    def update_price(self, start_time=None, end_time=None):
        """가격 정보를 업데이트 한다."""
        self.price.update(start_time=start_time, end_time=end_time)


@dataclass
class TickerAssetBase(AssetBase):
    ticker: str
