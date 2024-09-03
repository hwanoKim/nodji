import pandas as pd
from .file_utils import exists_path


def load_dataframe_file(file_path: str):
    """경로를 direct로 입력하여 load"""
    if exists_path(file_path):
        return pd.read_pickle(file_path)
    else:
        raise RuntimeError(f"The path: '{file_path}' is not existed.")


def save_dataframe_file(dataframe: pd.DataFrame, file_path: str):
    """경로를 direct로 입력하여 save."""
    try:
        dataframe.to_pickle(file_path)
    except Exception as e:
        raise RuntimeError(f"Failed to save dataframe to {file_path}. {e}")


def merge_dataframe_by_date(df_1, df_2):
    """두개의 dataframe을 병합한다. 겹치는 날짜는 제거한다."""
    df = pd.concat([df_1, df_2])
    df.sort_index(inplace=True)
    df = df[~df.index.duplicated(keep='last')]
    return df
