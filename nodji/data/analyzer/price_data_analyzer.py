from ...assets.coin.coin import Coin
import nodji as nd


class CoinPriceDataAnalyzer:
    def __init__(self, coin: 'Coin'):
        self._coin = coin

    def analyze_price_change(self, start_time: str = None, end_time: str = None, lookahead_minutes: int = 120):
        """특정 시간뒤의 가격 변동폭을 분석해준다

        설명:
            lookahead_minutes:
                특정시간 뒤의 가격변화가 어떻게 일어났는지 알려준다.
        """
        self._coin.price_data.load(start_time, end_time)
        df = self._coin.price_data._df

        df["future_price"] = df["Close"].shift(-lookahead_minutes)
        df["price_change"] = (df["future_price"] - df["Close"]).abs() / df["Close"] * 100  # 절대값 변동폭 (%)
        df = df.dropna(subset=["future_price"]).copy()

        mean_change = df["price_change"].mean()

        # 최대 상승폭 및 날짜
        max_change = df["price_change"].max()
        max_change_date = df[df["price_change"] == max_change].index[0]

        # 최대 하락폭 및 날짜 (최소값 기준)
        df["negative_change"] = (df["future_price"] - df["Close"]) / df["Close"] * 100
        min_change = df["negative_change"].min()  # 최소값은 음수일 수 있음
        min_change_date = df[df["negative_change"] == min_change].index[0]

        # 상승 및 하락 분리
        df["positive_change"] = (df["future_price"] - df["Close"]) / df["Close"] * 100
        over_5_positive = len(df[df["positive_change"] > 5]) / len(df) * 100
        over_10_positive = len(df[df["positive_change"] > 10]) / len(df) * 100

        over_5_negative = len(df[df["positive_change"] < -5]) / len(df) * 100
        over_10_negative = len(df[df["positive_change"] < -10]) / len(df) * 100

        # 결과 출력
        print("=" * 50)
        print(f"분석 기간: {nd.NTime(start_time)} ~ {end_time if nd.NTime(end_time) else nd.NTime.get_current_time()}")
        print(f"분석 대상: {self._coin.eng_name}")
        print(f"분석 간격: {lookahead_minutes}분 후 가격 변동")
        print("-" * 50)
        print(f"평균 변동폭: {mean_change:.4f}%")
        print(f"최대 상승폭: {max_change:.4f}% (날짜: {max_change_date})")
        print(f"최대 하락폭: {min_change:.4f}% (날짜: {min_change_date})")
        print(f"5% 이상 상승: {over_5_positive:.4f}%")
        print(f"10% 이상 상승: {over_10_positive:.4f}%")
        print(f"5% 이상 하락: {over_5_negative:.4f}%")
        print(f"10% 이상 하락: {over_10_negative:.4f}%")
        print("=" * 50)
