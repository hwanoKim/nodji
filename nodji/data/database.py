from .data import DataFrameData


class Database:
    """DatabaseManager는 asset들의 dataframe들을 저장하고 불러오는 용도를 가지고 있다."""

    def exists_dataframe(self, name):
        """asset들의 dataframe들이 있는지 확인한다."""
        return DataFrameData(name).exists

    def load_dataframe(self, name):
        """asset들의 dataframe들을 불러온다."""
        return DataFrameData(name).load()

    def save_dataframe(self, name, dataframe):
        """asset들의 dataframe들을 저장한다."""
        DataFrameData(name).save(dataframe)
