
import nodji as nd
nd.log(nd.LogLevel.DEBUG)

assets = nd.Assets()
coins = assets.coins
coin = coins['KRW-BTC']
coin.update_price('20240730', '20240905')
coin.price.load()

# print(coin.price)
