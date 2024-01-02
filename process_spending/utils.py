import calendar
import os
import re

import pandas as pd


def clean_fidelity_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Converts raw Fidelity data export the standard spending data structure
    """
    # Remove credit card repayments
    data = data[data["Transaction"] == "DEBIT"]
    data = data.drop(columns="Transaction")

    # Uses the 23 digit reference number as Id
    data["Memo"] = data["Memo"].apply(lambda x: re.findall(r"\d{23}", x)[0])
    data = data.rename(columns={"Memo": "Id"})

    # Rename columns
    data = data[["Id", "Date", "Name", "Amount"]]

    # Removes extra spaces in name
    data["Name"] = data["Name"].apply(lambda x: re.sub(r"\s+", " ", x))

    data = data.set_index("Id")
    data = data.groupby("Id").apply(lambda x: combine_id(x))

    return data


def clean_bank_of_america_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Converts raw Bank of America data export to the standard spending data structure
    """
    # Removes credit card repayments and ussage of rewards
    data = data[data["Amount"] < 0]
    data.drop(columns="Address")

    data = data.rename(
        columns={"Posted Date": "Date", "Reference Number": "Id", "Payee": "Name"}
    )
    data = data[["Id", "Date", "Name", "Amount"]]

    data["Date"] = pd.to_datetime(data["Date"])

    # Removes extra spaces in name
    data["Name"] = data["Name"].apply(lambda x: re.sub(r"\s+", " ", x))

    data = data.set_index("Id")
    data = data.groupby("Id").apply(lambda x: combine_id(x))

    return data


def combine_id(data: pd.DataFrame) -> pd.Series:
    """
    Combines transactions with the same Id.
    Uses the Date and Name of the orginally highest amount.
    """
    greatest_row = data.sort_values("Amount").iloc[0]
    greatest_row["Amount"] = data["Amount"].sum()

    return greatest_row


def read_folder_csv(folderpath: str) -> pd.DataFrame:
    """
    Reads all csv in folder and concats into a single dataframe.
    Assumes all csv share the same format.
    """
    dataframe_list = []

    for filename in os.listdir(folderpath):
        if filename.endswith(".csv"):
            file_path = os.path.join(folderpath, filename)
            df = pd.read_csv(file_path)
            dataframe_list.append(df)

    data = pd.concat(dataframe_list)

    return data


def month_mid(input_date):
    """
    For a given date time, find the middle of the month.
    """

    daysinmonth = calendar.monthrange(input_date.year, input_date.month)[1]

    return int(daysinmonth / 2 + 1)
