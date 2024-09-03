from dataclasses import dataclass
from ..assets.asset_base import TickerAssetBase
from ..data.price_datas.coin_price_data import CoinPriceData


@dataclass
class CoinMarketCaution:
    """upbit에서 각 코인에 제공하는 시장 경고 정보를 담고 있는 데이터 클래스이다."""
    price_fluctuations: bool = False
    trading_volume_soaring: bool = False
    deposit_amount_soaring: bool = False
    global_price_differences: bool = False
    concentration_of_small_accounts: bool = False


@dataclass
class Coin(TickerAssetBase):
    kor_name: str
    eng_name: str
    warning: bool
    caution: CoinMarketCaution = CoinMarketCaution()

    @property
    def price(self):
        """코인의 가격은 분단위 ohlcv 가격이다.

        분당이 아닌 가격은 현재는 생각하지 않고 있다. 어차피
        나는 실시간 정보를 기반으로 거래는 하지 않는 것을 생각하고 있다.
        """
        return CoinPriceData(self)
