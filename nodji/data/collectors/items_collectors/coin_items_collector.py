from .items_collector_base import AssetItemsCollectorBase
import nodji as nd


class CoinItemsCollector(AssetItemsCollectorBase):

    def get_from_upbit(self):
        ub = nd.external_apis.Upbit()
        return ub.get_market_codes()
