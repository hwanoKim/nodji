from ..assets.asset_base import AssetBase
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..assets.coin.coin import Coin


class BacktesterBase:
    def __init__(self, asset: AssetBase):
        self._asset = asset


class CoinBacktester(BacktesterBase):
    _asset: 'Coin'

    def run(self, start_time: str, end_time: str):
        pass
