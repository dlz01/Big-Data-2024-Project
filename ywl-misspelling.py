from spellchecker import SpellChecker
import pandas as pd
import re

spell = SpellChecker()


def load_test_dataset():
    return pd.read_csv("./datasets/Volunteers.csv")


def info(df: pd.DataFrame):
    """
    Look at each column along with some sample values
    """
    for column in df.columns:
        print(f"Column: {column}")
        print(f"Data Type: {df[column].dtype}")
        print("Sample Values:")
        print(df[column].head(), "\n")


def pre_processing(df: pd.DataFrame):
    """
    Convert the columns with dtype object to string
    """
    for column in df.columns:
        if df[column].dtype == "object":
            df[column] = df[column].astype("string")


def check_misspelling(line: str):
    """
    Check wheter there is misspelling in a line
    return:
        (true/false, list of potential misspelling words)
    """
    line = re.sub("[^a-zA-Z ]", "", line)
    line = re.sub(r"\s+", " ", line).strip()
    words = line.split(" ")
    candidates = spell.unknown(words=words)
    if candidates:
        return True, candidates
    else:
        return False, []


if __name__ == "__main__":
    # df = load_test_dataset()
    # pre_processing(df)
    # info(df)

    line = "Therre is!  a misseplling,'"
    exist, candidates = check_misspelling(line=line)
    if exist:
        print(candidates)
