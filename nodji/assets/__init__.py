from .coin.coins import Coins
from .asset_base import AssetsBase


class Assets:
    """모든 asset 시퀀스 클래스들을 가지고 있는 클래스이다."""

    def __init__(self):
        self.coins = Coins()

    def __repr__(self):
        return f"coins: {self.coins}\n"

    @property
    def _all_asset_sequences(self):
        """assets에 인스턴스 변수로 등록된 모든 asset 시퀀스들을 가져온다."""
        for assets in self.__dict__.values():
            if isinstance(assets, AssetsBase):
                yield assets

    def update_items(self):
        """종류별로 각 종목들을 업데이트 한다."""
        for assets in self._all_asset_sequences:
            assets.update_items()

    def update_price_datas(self):
        """모든 종목들의 가격을 업데이트 한다."""
        for assets in self._all_asset_sequences:
            assets.update_price()
