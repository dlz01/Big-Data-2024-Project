import pandas as pd
from misspell import misspell
from invalid_value import invalid_value
from null_value import null_value

def process(df, filters):
    df_out = pd.DataFrame()
    if 'Misspelling/Abbreviation' in filters:
        df, df_out = misspell(df, df_out)
    if 'Invalid value' in filters:
        df, df_out = invalid_value(df, df_out)
    if 'NULL value' in filters:
        df, df_out = null_value(df, df_out)
    return df, df_out