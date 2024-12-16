from typing import cast, TYPE_CHECKING

from .updaters.coin_price_updater import CoinPriceUpdater
from .asset_price_data_base import MinutePriceData, OHLCVData

if TYPE_CHECKING:
    from ...assets.coin.coin import Coin


class CoinPriceData(MinutePriceData, OHLCVData):
    _asset: 'Coin'

    @property
    def update(self):
        return CoinPriceUpdater(self)
