from dataclasses import asdict

import pandas as pd

from nodji.assets.coin import Coin, CoinMarketCaution
from nodji.data.converters.items_converters.items_converter_base import AssetItemsConverterBase


class CoinItemsConverter(AssetItemsConverterBase):
    def dataframe_to_asset_items(self, dataframe: pd.DataFrame) -> list['Coin']:
        if dataframe.empty:
            return []
        else:
            coins = []
            for _, row in dataframe.iterrows():
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

    def asset_items_to_dataframe(self, assets: list[Coin]) -> pd.DataFrame:
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
