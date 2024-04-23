from spellchecker import SpellChecker
import pandas as pd
import re

spell = SpellChecker()


def load_test_dataset():
    df = pd.read_csv("./datasets/Volunteers.csv")
    pre_processing(df)
    return df


def load_location():
    df = pd.read_csv("./datasets/NHoodNameCentroids.csv")
    df.drop(columns=["the_geom", "OBJECTID", "Stacked", "AnnoAngle"], inplace=True)
    pre_processing(df)
    return df


def flatten_location(df: pd.DataFrame) -> pd.DataFrame:
    """
    merge all columns as one columns and remove duplicates
    return:
        result: a location dictionary
    """
    cols = list(df.columns)
    result = pd.DataFrame(columns=["location"])
    for col in cols:
        data = (
            df[col]
            .astype("str")
            .str.lower()
            .replace("[^a-zA-Z]", " ", regex=True)
            .replace(r"\s+", " ", regex=True)
            .str.strip()
        )
        data.dropna(inplace=True)
        words = data.str.split(" ")
        words = words.explode()
        result = pd.concat(
            [result, words.rename("location").to_frame()], ignore_index=True
        )

    return result.dropna().drop_duplicates().reset_index(drop=True)


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


def check_misspelling(line: str, location: pd.DataFrame):
    """
    Check wheter there is misspelling in a line
    return:
        (true/false, list of potential misspelling words)
    """
    line = re.sub("[^a-zA-Z ]", " ", line)
    line = re.sub(r"\s+", " ", line).strip()
    words = line.split(" ")
    candidates = spell.unknown(words=words)
    if candidates:
        result = []
        print("Initially: " + str(candidates))
        for c in candidates:
            if c.lower() not in location["location"].values:
                result.append(c)
        print("After filtering out locations: " + str(result))
        if result:
            return True, result
        else:
            return False, []
    else:
        return False, []


def check_column_misspelling(df: pd.DataFrame, col_name: str, location: pd.DataFrame):
    """
    check each row of one column and add tag in a new column
    """
    df[col_name + ": Misspelling"] = False
    for _, row in df.iterrows():
        line = row[col_name]
        if not pd.isna(line):
            flag, candidates = check_misspelling(line=line, location=location)
            row[col_name + ": Misspelling"] = flag


if __name__ == "__main__":
    df = load_test_dataset()
    locations = load_location()
    locations = flatten_location(locations)
    # locations.to_csv("test.csv")
    # info(locations)
    # info(locations)
    check_column_misspelling(df, "NTA", locations)
    print(df[df["NTA: Misspelling"]])

    # print(type(df["NTA"]))
    # info(df)

    # line = "Therre is!  a misseplling,'"
    # exist, candidates = check_misspelling(line=line)
    # if exist:
    #     print(candidates)
