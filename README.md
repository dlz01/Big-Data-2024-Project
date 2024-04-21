# Big-Data-2024---Project

## TODO
Develop a semi-automated tool for classifying columns in a dataset into the following categories:
1. Valid value
2. Misspelling/Abbreviation
3. Invalid value
4. NULL value

## Misspelling/Abbreviation
1. Python pyspellchecker: Pairing words in dictionaries
2. Cluster/edit distance: If there is a word with low frequency but small edit distance to a correct word, it could be considered as misspelling.
3. Abbreviations dictionary (location/regular): If a word is considered misspelling, search abbreviation dictionary for that word

## Invalid Value
Clustering (KNN) for finding outliers: [Reference method](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=f28fb5ca7c8450a489e7d61fc0ca65079aa3700a)

## NULL value
Loop across dataset to find NULL or matching patterns (e.g., N/A, 999, 999-999-9999)
