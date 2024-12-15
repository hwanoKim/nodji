from dataclasses import asdict
import pandas as pd
from ....data.converters.asset_items_converters.asset_items_converter_base import AssetItemsConverterBase
from ....data.ndata.ndata import NData
from ....assets.coin.coin import Coin, CoinMarketCaution


class CoinItemsConverter(AssetItemsConverterBase):
    def ndata_to_asset_items(self, ndata: NData) -> list['Coin']:
        if ndata.is_empty:
            return []
        else:
            coins = []
            for row in ndata.rows:
                caution = CoinMarketCaution(**row['caution'])
                coin = Coin(
                    ticker=row['ticker'],
                    kor_name=row['kor_name'],
                    eng_name=row['eng_name'],
                    warning=row['warning'],
                    caution=caution
                )
                coins.append(coin)
            return coins

    def asset_items_to_dataframe(self, assets: list['Coin']) -> pd.DataFrame:
        """코인 객체들을 데이터프레임으로 변환한다.

        설명:
            asdict:
                dataclasses의 객체를 dict로 변환한다.
                예시로 아래와 같은 클래스가 있다면
                    @dataclass
                    class Coin:
                        name: str
                        value: float

                이렇게 변형된다.
                # 출력: {'name': 'Bitcoin', 'value': 30000.0}
        """
        return pd.DataFrame([asdict(asset) for asset in assets])

    def api_to_asset_items(self, coins: list[dict]) -> list['Coin']:
        return [Coin(ticker=coin['market'],
                     kor_name=coin['korean_name'],
                     eng_name=coin['english_name'],
                     warning=coin['market_event']['warning'],
                     caution=CoinMarketCaution(coin['market_event']['caution']['PRICE_FLUCTUATIONS'],
                                               coin['market_event']['caution']['TRADING_VOLUME_SOARING'],
                                               coin['market_event']['caution']['DEPOSIT_AMOUNT_SOARING'],
                                               coin['market_event']['caution']['GLOBAL_PRICE_DIFFERENCES'],
                                               coin['market_event']['caution']['CONCENTRATION_OF_SMALL_ACCOUNTS']))
                for coin in coins]
