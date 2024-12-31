import pandas as pd

from ...price_datas.asset_price_data_base import AssetPriceDataBase


class AssetPriceConverterBase:
    """asset의 price들을 변환하는 클래스의 부모 클래스이다."""

    def __init__(self, assets: 'AssetPriceDataBase'):
        self._assets = assets

    def api_to_dataframe(self, data: dict) -> pd.DataFrame:
        """api 데이터를 dataframe으로 변환한다."""
        raise NotImplementedError("api_to_dataframe method must be implemented in PriceConverterBase")