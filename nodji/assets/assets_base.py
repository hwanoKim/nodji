from typing import Sequence, Generic
from ..data import Database
from .asset_base import TickerAssetBase
from typing import TypeVar, Sequence, Generic, get_type_hints

T = TypeVar("T")


class AssetsBase(Sequence, Generic[T]):
    """asset 시퀀스 클래스들의 부모 클래스이다."""

    def __init__(self):
        """

        Notes:
            _asset_data_conv:
                데이터베이스에 저장된 데이터를 asset 객체로 변환하는 함수
        """
        self._assets: list[T] = []
        self._db = Database()
        self._load_assets()

    def __getitem__(self, item):
        asset_type = get_type_hints(self.__class__)['T'].__name__
        if isinstance(item, str):
            for asset in self._assets:
                if asset.name == item:
                    return asset
            else:
                raise KeyError(f"{asset_type} {item} not found")
        else:
            raise TypeError(f"{asset_type} name must be a string")

    def __len__(self):
        return len(self._assets)

    def __repr__(self):
        raise NotImplementedError(f"__repr__ method must be implemented in {self.__class__.__name__}")

    @property
    def _conv(self):
        """데이터 컨버터

        asset의 데이터를 db로
        db의 데이터를 asset으로
        api의 데이터를 asset으로

        이런종류의 변환을 담당하는 클래스
        """
        raise NotImplementedError(f"conv property must be implemented in {self.__class__.__name__}")

    def update(self):
        """어셋들의 리스트들을 업데이트 해준다."""
        raise NotImplementedError(f"update method must be implemented in {self.__class__.__name__}")

    def _load_assets(self):
        """어셋의 리스트들을 디비에서 읽어온다"""
        raise NotImplementedError(f"_load_assets method must be implemented in {self.__class__.__name__}")


class TickerAssetsBase(AssetsBase[TickerAssetBase]):
    """ticker asset 시퀀스 클래스들의 부모 클래스이다."""

    def __repr__(self):
        return ', '.join(self.tickers)

    def __getitem__(self, item):
        if isinstance(item, str):
            for asset in self._assets:
                if asset.ticker == item:
                    return asset
            else:
                raise KeyError(f"{self.__class__.__name__}")
        elif isinstance(item, (int, slice)):
            return self._assets[item]
        else:
            raise TypeError("ticker must be a string")

    @property
    def tickers(self):
        return [asset.ticker for asset in self._assets]
