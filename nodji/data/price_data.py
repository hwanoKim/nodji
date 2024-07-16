from ..assets.asset_base import AssetBase


class MinutePriceData:

    def __init__(self, asset: AssetBase):
        self._asset = asset
