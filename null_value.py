import pandas as pd

def remove_null_values(df):
    null_values = ['NULL', 'n/a', '999', '999-999-9999']
    for col in df.columns:
        df[col] = df[col].replace(null_values, pd.NA)
    df = df.dropna()
    return df

if __name__ == "__main__":
    df = pd.read_csv("your_dataset.csv")
    df_cleaned = remove_null_values(df)