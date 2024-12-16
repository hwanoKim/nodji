from ...assets.asset_base import TickerAssetsBase
from ...assets.coin.coin import Coin
from ...data.collectors.items_collectors.coin_items_collector import CoinItemsCollector
from ...data.converters.asset_items_converters.coin_items_converter import CoinItemsConverter


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

    def update_items(self):
        """종목을 업데이트 한다.

        설명:
            지우고 다시 만든다.
                기존 데이터에서 없어지는 것을 지우고 추가하는 작업을 하지 않는다.
                생각해보면 알겠지만 무의미한 일이다.
                항상 새롭게 전체 리스트를 서버에서 받아온다.
        """
        self._assets = self._items_conv.api_to_asset_items(self._items_coll.get_from_upbit())
        ndf = self._items_conv.asset_items_to_ndataframe(self._assets)
        self._data.set_ndataframe(ndf)
        self._data.save()
