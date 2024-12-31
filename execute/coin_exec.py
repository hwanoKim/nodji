import os
import nodji as nd
import pandas as pd
# pd.set_option('display.max_rows', None)
nd.log(nd.LogLevel.INFO)

assets = nd.Assets()
coins = assets.coins
coin = coins['KRW-BTC']
coin.update_price_data()
