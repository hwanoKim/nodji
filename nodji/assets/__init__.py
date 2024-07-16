from .coins import Coins
from .assets_base import AssetsBase


class Assets:
    """모든 asset 시퀀스 클래스들을 가지고 있는 클래스이다."""

    def __init__(self):
        self.coins = Coins()

    def update(self):
        for assets in self.__dict__.values():
            if isinstance(assets, AssetsBase):
                assets.update()
