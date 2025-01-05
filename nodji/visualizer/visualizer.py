import matplotlib.pyplot as plt
from ..assets.asset_base import AssetBase

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..assets.coin.coin import Coin


class VisualizerBase:
    def __init__(self, asset: AssetBase):
        self._asset = asset


class CoinVisualizer(VisualizerBase):
    _asset: 'Coin'

    def show(self):
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
        plt.plot(df.index, df["Close"], label=f"{self._asset.eng_name} Price", color="blue")
        plt.title(f"{self._asset.eng_name} Price Over Time", fontsize=16)
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Price (KRW)", fontsize=12)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()
