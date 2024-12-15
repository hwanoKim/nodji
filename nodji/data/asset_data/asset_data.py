from ..ndata.ndata import NData
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...assets import AssetsBase
    from ...assets.asset_base import AssetBase


class AssetData(NData):

    def __init__(self, asset: 'AssetBase'):
        super().__init__(asset._name)
        self._asset = asset


class AssetsData(NData):
    def __init__(self, assets: 'AssetsBase'):
        super().__init__(assets._name)
