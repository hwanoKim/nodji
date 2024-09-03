
import nodji as nd
nd.log(nd.LogLevel.DEBUG)

assets = nd.Assets()
coins = assets.coins
coin = coins['KRW-BTC']
# coin.update_price('20240830', '20240902')
print(coin.price.load())
