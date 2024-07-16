from dataclasses import asdict
from typing import TypeVar

import pandas as pd
from nodji.assets.coin import Coin, CoinMarketCaution

T = TypeVar('T')


class DataConverterBase:
    def api_to_assets(self, data: list[dict]) -> list[T]:
        raise NotImplementedError(f"{self.__class__.__name__}.api_to_assets")

    def assets_to_dataframe(self, assets: list[T]) -> pd.DataFrame:
        raise NotImplementedError(f"{self.__class__.__name__}.assets_to_dataframe")

    def dataframe_to_assets(self, dataframe) -> list[T]:
        raise NotImplementedError(f"{self.__class__.__name__}.dataframe_to_assets")


class CoinDataConverter(DataConverterBase):
    def dataframe_to_assets(self, dataframe: pd.DataFrame) -> list['Coin']:
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

    def assets_to_dataframe(self, assets: list[Coin]) -> pd.DataFrame:
        return pd.DataFrame([asdict(asset) for asset in assets])

    def api_to_assets(self, coins: list[dict]) -> list['Coin']:
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
