import pandas as pd
from misspell import misspell
from invalid_value import invalid_value
from null_value_check import null_value_check

def process(df, filters, columns):
    df_out = pd.DataFrame()
    if 'Misspelling/Abbreviation' in filters:
        df, df_out = misspell(df, df_out, columns)
    if 'Invalid value' in filters:
        df, df_out = invalid_value(df, df_out, columns)
    if 'NULL value' in filters:
        df, df_out = null_value_check(df, df_out, columns)
    return df, df_out