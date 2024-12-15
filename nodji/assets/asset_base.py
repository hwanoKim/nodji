from dataclasses import dataclass
from typing import Sequence

import nodji as nd
from ..data.price_datas.asset_price_data_base import AssetPriceDataBase
from ..data.asset_data.asset_data import AssetsData


@dataclass
class AssetBase:
    @property
    def price_data(self):
        return AssetPriceDataBase(self)

    def update_price(self, start_time=None, end_time=None):
        """가격 정보를 업데이트 한다."""
        self.price_data.update(start_time=start_time, end_time=end_time)


@dataclass
class TickerAssetBase(AssetBase):
    ticker: str


class AssetsBase(Sequence[AssetBase]):
    """asset 시퀀스 클래스들의 부모 클래스이다."""

    def __init__(self):
        """

        Notes:
            _asset_data_conv:
                데이터베이스에 저장된 데이터를 asset 객체로 변환하는 함수
        """
        self._assets = []
        self._data = AssetsData(self)
        self._load_asset_items()

    def __len__(self):
        return len(self._assets)

    def __repr__(self):
        raise NotImplementedError(f"__repr__ method must be implemented in {self.__class__.__name__}")

    @property
    def exists(self):
        return bool(self._assets)

    @property
    def _items_conv(self):
        """asset item 컨버터

        asset item들을 db로
        db의 데이터를 asset item으로
        api의 데이터를 asset item으로

        이런종류의 변환을 담당하는 클래스
        """
        raise NotImplementedError(f"conv property must be implemented in {self.__class__.__name__}")

    @property
    def _name(self):
        """asset 시퀀스의 이름"""
        raise NotImplementedError(f"name property must be implemented in {self.__class__.__name__}")

    def update_items(self):
        """어셋들의 종복 정보들을 업데이트 해준다."""
        raise NotImplementedError(f"update_item method must be implemented in {self.__class__.__name__}")

    def update_price(self):
        """어셋의 가격정보를 업데이트 한다."""
        for asset in self:
            asset.update_price()

    def _load_asset_items(self):
        """어셋의 리스트들을 디비에서 읽어온다"""
        self._assets = self._items_conv.ndataframe_to_asset_items(self._data.load())


class TickerAssetsBase(AssetsBase):
    """ticker asset 시퀀스 클래스들의 부모 클래스이다."""
    _assets: list[TickerAssetBase]

    def __repr__(self):
        if self.exists:
            return self._name + ': ' + ', '.join(self.tickers)
        else:
            return self._name + ': empty'

    def __getitem__(self, item):
        if isinstance(item, str):
            for asset in self._assets:
                if asset.ticker == item:
                    return asset
            else:
                raise KeyError(f"{item} is not in {self._name}")
        elif isinstance(item, (int, slice)):
            return self._assets[item]
        else:
            raise TypeError("ticker must be a string")

    @property
    def tickers(self):
        return [asset.ticker for asset in self._assets]
