from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....assets import AssetsBase


class AssetItemsCollectorBase:
    """가격 데이터를 수집하는 클래스"""

    def __init__(self, assets: 'AssetsBase'):
        self._assets = assets
