"""
coin을 분류한것은 순환 import를 막기 위해서이다.

Coins <- Coin
Coins <- CoinsDataConverter <- Coin

오류났던 과거는:
    coins.py 모듈에 Coins, Coin이 모두 있었다.
    이 파일에서 CoinsDataConverter을 불렀어야 했으나
    CoinsDataConverter에서도 Coin을 불러서 사용했어야 했다.
"""

from .coin import Coin
from .assets_base import TickerAssetsBase
from ..data.converters.items_converters.coin_items_converter import CoinItemsConverter
from ..data.collectors.items_collectors.coin_items_collector import CoinItemsCollector
import nodji as nd


class Coins(TickerAssetsBase):
    _assets: list[Coin]

    def __init__(self):
        super().__init__()

    @property
    def _name(self):
        return 'coins'

    @property
    def _items_conv(self):
        return CoinItemsConverter(self)

    @property
    def _items_coll(self):
        return CoinItemsCollector(self)

    def update_item(self):
        """종목을 업데이트 한다.

        설명: 지우고 다시 만든다.
            기존 데이터를 지우고 추가하는 작업을 하지 않는다.
            생각해보면 무의미한 일이다.
            항상 새롭게 전체 리스트를 서버에서 받아온다.
        """
        self._assets = self._items_conv.api_to_asset_items(self._items_coll.get_from_upbit())
        df = self._items_conv.asset_items_to_dataframe(self._assets)
        self._data(df)
        self._data.save()
