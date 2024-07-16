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
from ..data.asset_data_converter import CoinDataConverter
import nodji as nd


class Coins(TickerAssetsBase[Coin]):
    def __init__(self):
        super().__init__()
        self._ub = nd.external_apis.Upbit()

    @property
    def _conv(self):
        return CoinDataConverter()

    def update(self):
        self._assets = self._conv.api_to_assets(self._ub.get_market_codes())
        df = self._conv.assets_to_dataframe(self._assets)
        self._db.save_dataframe('coins', df)

    def _load_assets(self):
        self._assets = self._conv.dataframe_to_assets(self._db.load_dataframe('coins'))
