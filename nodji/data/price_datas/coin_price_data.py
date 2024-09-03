from typing import cast, TYPE_CHECKING

import pandas as pd
import nodji as nd

from ..updaters.coin_price_updater import CoinPriceUpdater
from .asset_price_data_base import MinutePriceData, OHLCVData

if TYPE_CHECKING:
    from ...assets.coin import Coin
    from ...common.ntime import NTime


class CoinPriceData(MinutePriceData, OHLCVData):
    @property
    def _coin(self) -> 'Coin':
        from ...assets.coin import Coin
        return cast(Coin, self._asset)

    @property
    def update(self):
        return CoinPriceUpdater(self)

    def load(self):
        self._data.load()
