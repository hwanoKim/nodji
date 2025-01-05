import nodji as nd
import pandas as pd
pd.set_option('display.max_rows', 10)
nd.log(nd.LogLevel.INFO)

start_time = '250101'

assets = nd.Assets()
coin = assets.coins['KRW-BTC']
anlzr = nd.CoinPriceDataAnalyzer(coin)
anlzr.analyze_price_change(start_time=start_time,
                           lookahead_minutes=60)
coin.show(start_time)

