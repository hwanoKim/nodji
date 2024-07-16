from dataclasses import dataclass
from nodji.assets.asset_base import TickerAssetBase


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
