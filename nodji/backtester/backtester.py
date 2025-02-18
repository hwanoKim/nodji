from dataclasses import dataclass

from ..assets.asset_base import AssetBase
from typing import TYPE_CHECKING
from .evaluators.evaluators import _EvaluatorBase
import nodji as nd

if TYPE_CHECKING:
    from ..assets.coin.coin import Coin


@dataclass
class BacktestConfig:
    """백테스트를 위한 설정을 담고 있는 데이터 클래스이다.

    Attributes:
        initial_cash:
            최초 보유 금액
        start_time:
            백테스트 시작 시간
        end_time:
            백테스트 종료 시간

        lookahead_steps:
            백테스트에서 미래를 예측할 때 사용하는 스텝 수
        target_multiplier:
            목표 수익률. lookahead_steps 이내의 시간 동안 이 수익률을 달성하면 전략의 성공이라고 판단

        buy_threshold:
            매수 신호를 받기 위한 임계값
        sell_threshold:
            매도 신호를 받기 위한 임계값
    """
    initial_cash: float = 100_000
    start_time: str = None
    end_time: str = None

    lookahead_steps: int = 60 * 3
    target_multiplier: float = 1.02

    buy_threshold: float = 0.6
    sell_threshold: float = 0.2


class BacktestReport:
    def __init__(self, config: BacktestConfig, trades: 'Trades'):
        self.config = config
        self.trades = trades

    def summary(self):
        pass

    def plot(self):
        pass


class BacktesterBase:
    def __init__(self, asset: AssetBase):
        self._asset = asset


class Trades:
    pass


class CoinBacktester(BacktesterBase):
    _asset: 'Coin'

    def backtest(self, evaluators: list[_EvaluatorBase], config: BacktestConfig = None) -> BacktestReport:
        """evaluator들의 전략으로 수익을 계산한다"""
        if config is None:
            config = BacktestConfig()

        self._asset.price_data.load(nd.NTime(config.start_time), nd.NTime(config.end_time))
        self._trades = self._generate_trades(evaluators, config)
        return BacktestReport(config, self._trades)
        # self._pf_flow = PortfolioFlow(self._asset,
        #                               start_time=nd.NTime(config.start_time),
        #                               end_time=nd.NTime(config.end_time),
        #                               trades=self._trades)

    def _generate_trades(self, evaluators: list[_EvaluatorBase], config: BacktestConfig) -> Trades:
        """evaluator들로 벡테스트 결과를 계산하여 반환한다"""
        return Trades()

    # def calculate_price_change(self, config: BacktestConfig = None):
    #     """첫 시간의 금액이 마지막 시간에 얼마가 되는지 단순하게 계산한다"""
    #     if config is None:
    #         config = BacktestConfig()
    #
    #     self._asset.price_data.load(config.start_time, config.end_time)
    #     df = self._asset.price_data._df
    #     start_price = df.iloc[0]['Close']
    #     end_price = df.iloc[-1]['Close']
    #
    #     final_value = config.initial_cash * (end_price / start_price)
    #
    #     profit_loss = final_value - config.initial_cash
    #     profit_loss_percentage = (profit_loss / config.initial_cash) * 100
    #
    #     end_time = config.end_time if nd.NTime(config.end_time) else nd.NTime.get_current_time()
    #
    #     print("=" * 50)
    #     print("백테스트 결과")
    #     print("-" * 50)
    #     print(f"분석 기간: {nd.NTime(config.start_time)} ~ {end_time}")
    #     print("-" * 50)
    #     print(f"초기 금액: {config.initial_cash:,.0f}원")
    #     print(f"시작 가격: {start_price:,.2f}")
    #     print(f"종료 가격: {end_price:,.2f}")
    #     print(f"최종 금액: {final_value:,.0f}원")
    #     print(f"수익/손실: {profit_loss:,.0f}원 ({profit_loss_percentage:.2f}%)")
    #     print("=" * 50)
