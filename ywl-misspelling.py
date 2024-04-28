from spellchecker import SpellChecker
import pandas as pd
import re
from collections import Counter
from edit_distance import edit_distance
from clustering import hierarchical_clustering

spell = SpellChecker()


def load_test_dataset():
    df = pd.read_csv("./datasets/Volunteers-misspelled.csv")
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
        # print("Initially: " + str(candidates))
        for c in candidates:
            if c.lower() not in location["location"].to_numpy():
                result.append(c)
        # print("After filtering out locations: " + str(result))
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
            if flag is True:
                threshold = int(df[col_name].count() / 200)
                for candidate in candidates:
                    frequency = check_frequency(candidate, df, col_name)
                    if frequency < threshold:
                        flag = True
                        break
                    else:
                        flag = False
            if flag is True:
                print(col_name + " misspelling: " + " ".join(candidates))
            row[col_name + ": Misspelling"] = flag


def check_frequency(word: str, df: pd.DataFrame, col_name: str):
    col = pd.DataFrame(df[col_name])
    col = (
        col[col_name]
        .astype("str")
        .str.lower()
        .str.replace("[^a-zA-Z]", " ", regex=True)
        .replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    col.dropna(inplace=True)
    col = col.str.split(" ")
    col = col.explode()
    frequency = (col == word.lower()).sum()
    return frequency


def clustering_misspelling_check(df: pd.DataFrame, col_name: str):
    """
    check misspelling using the heuristic method:
    clustering the words, the word with low frequency within a cluster might be misseplling
    """
    words = df[col_name].dropna().to_list()
    words = list(map(lambda x: re.sub("[^a-zA-Z ]", " ", x), words))
    words = list(map(lambda x: re.sub(r"\s+", " ", x).strip(), words))
    words = list(map(lambda x: x.lower(), words))
    words = list(map(lambda x: x.split(" "), words))
    flatten_words = []
    for word_list in words:
        for word in word_list:
            flatten_words.append(word)
    cluster_dict = hierarchical_clustering(words=flatten_words, dist=edit_distance)
    # cluster_dict = {cluster_label: [words]}
    for _, cluster in cluster_dict.items():
        counter = Counter(cluster)
        print(counter)


if __name__ == "__main__":
    df = load_test_dataset()
    locations = load_location()
    locations = flatten_location(locations)
    check_column_misspelling(df, "NTA", locations)
    # clustering_misspelling_check(df, "NTA")
    # print(check_frequency("cuty", df, "NTA"))
