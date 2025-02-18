import nodji as nd
import backtesting

# pd.set_option('display.max_rows', 999999)
nd.log(nd.LogLevel.INFO)

assets = nd.Assets()
coin = assets.coins['KRW-BTC']
coin.update_price_data()

bt = nd.CoinBacktester(coin)
config = nd.BacktestConfig()
config.start_time = '241101'
config.initial_cash = 100_000

report = bt.backtest([], config)
report.summary()
report.plot()

# coin.load_price_data(config.start_time)
# coin.show()


# config = nd.BacktestConfig()
# config.start_time = '241101'
# config.target_multiplier = 1.02
# config.lookahead_steps = 60 * 24 * 3

# bt.backtest_with_evaluators(
#     [nd.evaluators.MovingAveragePositionEvaluator(60 * 24)],
#     config)
#
# # coin.load_price_data(config.start_time)
# # coin.show()
