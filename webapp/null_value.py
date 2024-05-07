import pandas as pd

def null_value(df, df_out):
    mask = df.isna().any(axis=1)

    filtered_out = df[mask]
    filtered = df[~mask]
    filtered_out = pd.concat([filtered_out, df_out], ignore_index=True)
    return filtered, filtered_out