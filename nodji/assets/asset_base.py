from dataclasses import dataclass


@dataclass
class AssetBase:
    def update_price(self):
        """가격 정보를 업데이트 한다."""
        raise NotImplementedError(f"update_price method must be implemented in {self.__class__.__name__}")


@dataclass
class TickerAssetBase(AssetBase):
    ticker: str
