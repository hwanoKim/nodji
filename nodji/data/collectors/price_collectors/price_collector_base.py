from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...price_datas.asset_price_data_base import AssetPriceDataBase
    from nodji.data.ndata._ndata import DataFrameData


class AsssetPriceCollectorBase:
    """가격 데이터를 수집하는 클래스"""

    def __init__(self, price_data: 'AssetPriceDataBase'):
        self._price_data = price_data
        self._data: 'DataFrameData' = price_data._data

    @property
    def _conv(self):
        raise NotImplementedError("conv property must be implemented in PriceCollectorBase")
