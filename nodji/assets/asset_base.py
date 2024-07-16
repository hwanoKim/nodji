from dataclasses import dataclass



@dataclass
class AssetBase:
    pass


@dataclass
class TickerAssetBase:
    ticker: str

