from cycler import cycler
from matplotlib import pyplot as plt

from nodji.assets.asset_base import AssetBase
from nodji.visualizer.visualizer_base import VisualizerBase
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..assets.coin.coin import Coin


class AssetVisualizer(VisualizerBase):

    def __init__(self, asset: AssetBase):
        self._asset = asset

    def show(self):
        """어셋들의 데이터를 그래프로 보여준다."""
        raise NotImplementedError(f"show method must be implemented in {self.__class__.__name__}")


class CoinVisualizer(AssetVisualizer):
    _asset: 'Coin'

    def show(self, additional_columns: list[str] = None):
        """가격 데이터를 시각화한다.

        설명:
            figure:
                가로를 10인치 세로를 6인치로 새 그래프를 생성
            legend:
                그래프에 범례(x축, y축)를 표시
            tight_layout:
                그래프의 여백을 최소화
        """
        df = self._asset.price_data._df

        plt.figure(figsize=(10, 6))
        plt.gca().set_prop_cycle(cycler(color=['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink']))
        plt.plot(df.index, df["Close"], label=f"{self._asset.eng_name} Price")

        if additional_columns:
            for col in additional_columns:
                if col in df.columns:
                    plt.plot(df.index, df[col], label=col)

        plt.title(f"{self._asset.eng_name} Price Over Time", fontsize=16)
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Price (KRW)", fontsize=12)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()
