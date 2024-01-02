import calendar
import os
import re
from typing import Callable

import pandas as pd

COL_NAMES = ["Id", "Date", "Name", "Amount"]

FIDELITY_COLUMN_MAP = {"Memo": "Id"}
FIDELITY_COL_FUNC = {
    "Id": lambda x: re.findall(r"\d{23}", x)[0],
    "Name": lambda x: re.sub(r"\s+", " ", x),
}

BA_COLUMN_MAP = {"Posted Date": "Date", "Reference Number": "Id", "Payee": "Name"}
BA_COL_FUNC = {
    "Name": lambda x: re.sub(r"\s+", " ", x),
    "Date": lambda x: pd.to_datetime(x).strftime("%Y-%m-%d"),
}


def set_col_names(
    data: pd.DataFrame, col_map: dict[str, str], col_names: list[str]
) -> pd.DataFrame:
    return data.rename(columns=col_map)[col_names]


def filter_debit(data: pd.DataFrame) -> pd.DataFrame:
    return data[data["Amount"] < 0]


def map_cols(data: pd.DataFrame, col_func: dict[str, Callable]) -> pd.DataFrame:
    for col, func in col_func.items():
        data[col] = data[col].map(func)
    return data


def clean_spending_data(
    filepath: str,
    col_map: dict[str, str],
    col_names: list[str],
    col_func: dict[str, Callable],
) -> pd.DataFrame:
    data = pd.read_csv(filepath)

    data = set_col_names(data, col_map, col_names)
    data = filter_debit(data)
    data = map_cols(data, col_func)

    data = data.set_index("Id")
    data = data.groupby("Id").apply(lambda x: total_duplicate(x))

    return data


def clean_fidelity(filepath: str) -> pd.DataFrame:
    data = clean_spending_data(
        filepath, FIDELITY_COLUMN_MAP, COL_NAMES, FIDELITY_COL_FUNC
    )

    return data


def clean_ba(filepath: str) -> pd.DataFrame:
    data = clean_spending_data(filepath, BA_COLUMN_MAP, COL_NAMES, BA_COL_FUNC)

    return data


def total_duplicate(data: pd.DataFrame) -> pd.Series:
    """
    Combines transactions with the same Id.
    Uses the Date and Name of the orginally highest amount.
    """
    greatest_row = data.sort_values("Amount").iloc[0]
    greatest_row["Amount"] = data["Amount"].sum()

    return greatest_row


def read_folder_csv(folderpath: str, load_func: Callable) -> pd.DataFrame:
    """
    Reads all csv in folder and concats into a single dataframe.
    Assumes all csv share the same format.
    """
    dataframe_list = []

    for filename in os.listdir(folderpath):
        if filename.endswith(".csv"):
            file_path = os.path.join(folderpath, filename)
            df = load_func(file_path)
            dataframe_list.append(df)

    data = pd.concat(dataframe_list)

    return data


def month_mid(input_date):
    """
    For a given date time, find the middle of the month.
    """

    daysinmonth = calendar.monthrange(input_date.year, input_date.month)[1]

    return int(daysinmonth / 2 + 1)
