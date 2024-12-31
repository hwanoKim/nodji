from typing import cast, TYPE_CHECKING

from .updaters.coin_price_updater import CoinPriceUpdater
from .asset_price_data_base import MinutePriceData, OHLCVData

if TYPE_CHECKING:
    from ...assets.coin.coin import Coin


class CoinPriceData(MinutePriceData, OHLCVData):

    def _set_updater(self):
        self.update = CoinPriceUpdater(self)
