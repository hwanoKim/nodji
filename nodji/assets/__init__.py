from .coins import Coins
from .assets_base import AssetsBase


class Assets:
    """모든 asset 시퀀스 클래스들을 가지고 있는 클래스이다."""

    def __init__(self):
        self.coins = Coins()

    @property
    def _all_assets(self):
        for assets in self.__dict__.values():
            if isinstance(assets, AssetsBase):
                yield assets

    def update(self):
        """모든 asset 관련된 정보들을 업데이트 한다."""
        self.update_item()
        self.update_price()

    def update_item(self):
        """종류별로 각 종목들을 업데이트 한다."""
        for assets in self._all_assets:
            assets.update_item()

    def update_price(self):
        """모든 종목들의 가격을 업데이트 한다."""
        for assets in self._all_assets:
            assets.update_price()
