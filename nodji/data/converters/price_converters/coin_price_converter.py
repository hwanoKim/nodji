import pandas as pd
import requests
import nodji as nd
from .asset_price_converter_base import AssetPriceConverterBase


class CoinPriceConverter(AssetPriceConverterBase):
    def api_to_dataframe(self, response: requests.Response) -> pd.DataFrame:
        df = pd.DataFrame(response.json())
        df = df[['candle_date_time_kst',
                 'opening_price',
                 'high_price',
                 'low_price',
                 'trade_price',
                 'candle_acc_trade_price',
                 'candle_acc_trade_volume']]
        df.rename(columns={'candle_date_time_kst': 'date',
                           'opening_price': 'Open',
                           'high_price': 'High',
                           'low_price': 'Low',
                           'trade_price': 'Close',
                           'candle_acc_trade_price': 'TradePrice',
                           'candle_acc_trade_volume': 'Volume'}, inplace=True)
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%dT%H:%M:%S', errors='raise')
        df['date'] = df['date'].dt.tz_localize(nd.TimeZone.SEOUL.value)
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)
        return df


