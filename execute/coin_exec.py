import nodji as nd

# pd.set_option('display.max_rows', 999999)
nd.log(nd.LogLevel.INFO)

assets = nd.Assets()
coin = assets.coins['KRW-BTC']

bt = nd.CoinBacktester(coin)
config = nd.BacktestConfig()
config.start_time = '241101'
config.initial_cash = 100_000

bt.backtest(
    [nd.evaluators.MovingAveragePositionEvaluator(60 * 24)],
    config)

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
