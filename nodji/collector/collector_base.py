from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..data.price_data import PriceDataBase


class AsssetPriceCollectorBase:
    """가격 데이터를 수집하는 클래스"""

    def __init__(self, price_data: 'PriceDataBase'):
        self._price_data = price_data
