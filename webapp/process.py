import pandas as pd
from misspell import misspell
from invalid_value import invalid_value
from null_value_check import null_value_check

def process(df, filters, columns):
    origin_df = df.copy()
    df_out = pd.DataFrame()
    if 'Misspelling/Abbreviation' in filters:
        df = misspell(df, columns)
    if 'Invalid value' in filters:
        df = invalid_value(df, columns)
    if 'NULL value' in filters:
        df = null_value_check(df, columns)

    df_out = origin_df.merge(df, indicator=True, how='outer').query('_merge == "left_only"').drop('_merge', axis=1)
    return df, df_out