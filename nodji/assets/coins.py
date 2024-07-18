"""
coin을 분류한것은 순환 import를 막기 위해서이다.

Coins <- Coin
Coins <- CoinsDataConverter <- Coin

오류났던 과거는:
    coins.py 모듈에 Coins, Coin이 모두 있었다.
    이 파일에서 CoinsDataConverter을 불렀어야 했으나
    CoinsDataConverter에서도 Coin을 불러서 사용했어야 했다.
"""

from nodji.assets.coin import Coin
from .assets_base import TickerAssetsBase
from ..data.asset_items_converter import CoinItemsConverter
import nodji as nd


class Coins(TickerAssetsBase):
    _assets: list[Coin]

    def __init__(self):
        super().__init__()
        self._ub = nd.external_apis.Upbit()

    @property
    def _name(self):
        return 'coins'

    @property
    def _items_conv(self):
        return CoinItemsConverter()

    def update_item(self):
        """종목을 업데이트 한다.

        기존에 저장해둔 항목들을 읽어서 업데이트 하지 않는다.
        항상 전체 리스트를 서버에서 받아온다.
        """
        self._assets = self._items_conv.api_to_asset_items(self._ub.get_market_codes())
        df = self._items_conv.asset_items_to_dataframe(self._assets)
        self._data.save(df)
