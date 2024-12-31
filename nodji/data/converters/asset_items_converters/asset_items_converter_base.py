from typing import TYPE_CHECKING

import pandas as pd

from nodji.data.ndata.ndata import NData
if TYPE_CHECKING:
    from ....assets import AssetsBase


class AssetItemsConverterBase:
    """asset의 item들을 변환하는 클래스의 부모 클래스이다."""

    def __init__(self, assets: 'AssetsBase'):
        self._assets = assets

    def api_to_asset_items(self, data: list[dict]):
        raise NotImplementedError(f"{self.__class__.__name__}.api_to_assets")

    def asset_items_to_dataframe(self, assets) -> pd.DataFrame:
        raise NotImplementedError(f"{self.__class__.__name__}.assets_to_ndata")

    def dataframe_to_asset_items(self, dataframe: pd.DataFrame):
        raise NotImplementedError(f"{self.__class__.__name__}.ndata_to_assets")
