import requests


class Upbit:

    def get_market_codes(self) -> list[dict]:
        """https://docs.upbit.com/reference/%EB%A7%88%EC%BC%93-%EC%BD%94%EB%93%9C-%EC%A1%B0%ED%9A%8C"""
        url = "https://api.upbit.com/v1/market/all?isDetails=true"
        headers = {"accept": "application/json"}
        res = requests.get(url, headers=headers)
        return res.json()
