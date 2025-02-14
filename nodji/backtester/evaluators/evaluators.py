import pandas as pd
from .. import indicators as _inds


class _EvaluatorBase:
    """평가의 기본 클래스"""

    def evaluate_weight_for_current_state(self, df: pd.DataFrame,
                                          lookahead_steps: int = 60 * 3, target_multiplier: float = 1.02) -> float:
        """각 전략에 따라서 현재의 상태를 판단하고 전략의 성공 가중치를 계산한다.

        설명:
            각 전략의 결과에 가중치를 부여한다.
            가중치는 -1 ~ 1 사이의 값으로 변환된다.
        """
        raise NotImplementedError


class MovingAveragePositionEvaluator(_EvaluatorBase):
    """이동평균 평가

    설명:
        state:
            가격이 이동평균선의 위인가 아래인가
    """

    def __init__(self, window: int = 60 * 12):
        self.window = window

    def evaluate_weight_for_current_state(self, df: pd.DataFrame,
                                          lookahead_steps: int = 60 * 3, target_multiplier: float = 1.02) -> float:
        """현재 상태 따른 weight를 계산하여 반환한다."""
        df = df.copy()
        ind = _inds.MovingAverageIndicator(self.window)
        ind.add_to_dataframe(df)

        state = self._get_current_state(ind, df)
        state_rows = self._get_state_rows(df, ind, state)

        lookahead_timedelta = pd.Timedelta(minutes=lookahead_steps)
        state_rows = state_rows.copy()
        state_rows['TargetTime'] = state_rows.index + lookahead_timedelta
        state_rows = state_rows[state_rows['TargetTime'] <= df.index[-1]]
        state_rows['TargetPrice'] = state_rows['Close'] * target_multiplier

        future_max_prices = df['Close'].rolling(f"{lookahead_steps}min", closed='right').max()

        # # 목표 가격을 초과하는지 여부 확인
        # state_rows['Success'] = future_max_prices.loc[state_rows.index] >= state_rows['TargetPrice']
        #
        # # 성공률 계산
        # success_count = state_rows['Success'].sum()
        # total_count = len(state_rows)
        #
        # weight = 0 if total_count == 0 else (success_count / total_count) * 2 - 1
        #
        # return weight
        #     target_price = state_rows.loc[index, 'Close'] * target_multiplier
        #     future_values = df.loc[index:index + lookahead_steps, 'Close']
        #     if (future_values >= target_price).any():
        #         success_count += 1
        #
        # total_count = len(state_rows)
        # weight = 0 if total_count == 0 else (success_count / total_count) * 2 - 1
        #
        # return weight
        # if state:
        #     true_rows = calc_df[calc_df['Close'] > calc_df[ind.name]]
        # else:
        #     true_rows = calc_df[calc_df['Close'] <= calc_df[ind.name]]
        #
        # future_prices = true_rows['Close'].shift(-lookahead_steps)
        # current_close = true_rows['Close'].iloc[:-lookahead_steps]
        # future_prices = future_prices.dropna()
        #
        # success = (future_prices >= current_close * target_multiplier)
        # success_count = success.sum()
        # total_count = len(future_prices)
        #
        # success_rate = success_count / total_count if total_count > 0 else 0
        # return 2 * success_rate - 1

    def _get_state_rows(self, df, ind, state):
        """같은 상태였던 row들을 반환"""
        return df[df['Close'] > df[ind.name]] if state else df[df['Close'] <= df[ind.name]]

    def _get_current_state(self, indicator, dataframe: pd.DataFrame) -> bool:
        """위면 True, 아래면 False"""
        return dataframe['Close'].iloc[-1] > dataframe[indicator.name].iloc[-1]