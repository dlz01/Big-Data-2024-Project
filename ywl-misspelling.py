from spellchecker import SpellChecker
import pandas as pd
import re
from collections import Counter
from edit_distance import edit_distance
from clustering import hierarchical_clustering

spell = SpellChecker()


def load_test_dataset():
    # df = pd.read_csv("./datasets/Volunteers-misspelled.csv")
    df = pd.read_csv("./datasets/VolunteersMisspelling.csv")
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
    for index, row in df.iterrows():
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
            # row[col_name + ": Misspelling"] = flag
            df.at[index, col_name + ": Misspelling"] = flag


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


def show_tags(df: pd.DataFrame, col_name: str, tag_name: str):
    """
    Show the tag of one column and show the original column if the tag is true
    """
    for _, row in df.iterrows():
        tag = row[col_name + ": " + tag_name]
        if not pd.isna(tag):
            # print(tag)
            if tag is True:
                print(row[col_name])


def check_accuracy(df: pd.DataFrame):
    col_name = "NTA"
    tag_name = "Misspelling"
    num_misspelling = 6
    total = df[col_name].count()
    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0
    misspelling = [
        "Batteru Park City-Lower Manhattan",
        "Van Cortlandt Villafe",
        "SoHo-TriBeCa-Civic Center-Littl Italy",
        "Crown Hights North",
        "Huntors Point-Sunnyside-West Maspeth",
        "Mariner's Habor-Arlington-Port Ivory-Graniteville",
        "Eeast Flushing",
    ]
    for index, row in df.iterrows():
        tag = row[col_name + ": " + tag_name]
        nta = row[col_name]
        if tag is True:
            # print(nta)
            if nta in misspelling:
                true_positive += 1
            else:
                false_positive += 1
        else:
            if pd.isna(nta):
                true_negative += 1
            elif nta in misspelling:
                print(nta)
                false_negative += 1
            else:
                true_negative += 1
    true_positive_rate = true_positive / (true_positive + false_negative)
    true_negative_rate = true_negative / (true_negative + false_positive)
    false_positive_rate = false_positive / (false_positive + true_negative)
    false_negative_rate = false_negative / (false_negative + true_positive)
    accuracy = (true_positive + true_negative) / (
        true_positive + true_negative + false_positive + false_negative
    )

    print("True Positive Count:", true_positive)
    print("True Negative Count:", true_negative)
    print("False Positive Count:", false_positive)
    print("False Negative Count:", false_negative)

    print("True Positive Rate (Sensitivity or Recall):", true_positive_rate)
    print("True Negative Rate (Specificity):", true_negative_rate)
    print("False Positive Rate (Fall-out):", false_positive_rate)
    print("False Negative Rate (Miss Rate):", false_negative_rate)
    print("Accuracy:", accuracy)


if __name__ == "__main__":
    df = load_test_dataset()
    locations = load_location()
    locations = flatten_location(locations)
    check_column_misspelling(df, "NTA", locations)
    # show_tags(df, "NTA", "Misspelling")
    check_accuracy(df)
