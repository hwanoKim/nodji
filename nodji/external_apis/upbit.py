import time
from typing import Optional

import pandas as pd
import requests
import nodji as nd
from nodji import NTime
from loguru import logger


class Upbit:

    def get_market_codes(self) -> list[dict]:
        """https://docs.upbit.com/reference/%EB%A7%88%EC%BC%93-%EC%BD%94%EB%93%9C-%EC%A1%B0%ED%9A%8C"""
        url = "https://api.upbit.com/v1/market/all?isDetails=true"
        headers = {"accept": "application/json"}
        res = requests.get(url, headers=headers)
        return res.json()

    def get_minute_candles(self, ticker: str, end_time: Optional[NTime]) -> requests.Response:
        """upbit에서 최대 날짜 범위의 mdata를 받아온다

        Notes:
            시간대:
                upbit에 querystring으로 호출하는 시간대는 utc 시간대이다.
                response된 값은
                candle_date_time_utc
                candle_date_time_kst
                두가지로 나오므로 한국시간대를 저장한다.

            sleep구문:
                값을 받을 때 에러나는 경우가 있다.
                max retries exceeded with url
                그럴경우 잠시 쉬어준다.

            1초를 더하는 이유:
                12시 10분 데이터를 받는다고 하면 12시 9분 데이터부터 나오는것 같다.
                그래서 1초를 더해주면 12시 10분 데이터가 포함되어 나온다.
        """
        if end_time is None:
            end_time = nd.NTime.get_current_time()
        assert isinstance(end_time, NTime), f"end_date must be NTime but {type(end_time)}"
        end_time.sec += 1
        url = "https://api.upbit.com/v1/candles/minutes/1"
        try:
            querystring = {"market": ticker,
                           "to": end_time.to_utc().to_string(),
                           "count": str(nd.consts.Upbit.MAX_UPBIT_MPRICE_QUERY_COUNT)}
            headers = {"accept": "application/json"}
            response = requests.get(url, params=querystring, headers=headers)
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
            logger.debug(f"Something wrong. end_date: {end_time}.")
            return self.get_minute_candles(ticker, end_time)

        if response.status_code == 429:
            time.sleep(0.1)
            logger.debug('Too many request')
            return self.get_minute_candles(ticker, end_time)

        logger.debug(f"upbit response: {response.json()[-1]['candle_date_time_kst']}")
        return response
