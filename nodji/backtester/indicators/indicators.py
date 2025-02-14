import pandas as pd


class _IndicatorBase:
    name: str

    def add_to_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError


class MovingAverageIndicator(_IndicatorBase):
    name: str = 'MA'

    def __init__(self, window: int = 60):
        self.window = window

    def add_to_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        dataframe[self.name] = dataframe['Close'].rolling(window=self.window,
                                                          min_periods=self.window).mean()
        return dataframe
