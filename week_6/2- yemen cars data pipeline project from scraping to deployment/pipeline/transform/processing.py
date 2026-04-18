import pandas as pd
from pathlib import Path

raw_csv = Path("data/raw/yemen_cars.csv")
processed_dir = Path("data/processed")
processed_csv = processed_dir / "yemen_cars_cleaned.csv"


def drop_nullvalues_in_name(df):
    return df[df["name"].notna()]


def drop_duplicate_data(df):
    return df.drop_duplicates()


def clean_price(df):
    df = df.copy()
    df["price"] = df["price"].replace(r"[^\d.]", "", regex=True)
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["price"] = df["price"].fillna(df["price"].median())
    return df


def clean_text_columns(df):
    df = df.copy()
    text_columns = ["name", "description", "status", "location", "country"]

    for column in text_columns:
        if column in df.columns:
            df[column] = df[column].astype("string").str.strip()
            df[column] = df[column].replace({"": pd.NA, "nan": pd.NA})

    return df


def clean_numeric_columns(df):
    df = df.copy()

    for column in ["model", "mileage"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def clean_posted_at(df):
    df = df.copy()
    if "posted_at" in df.columns:
        df["posted_at"] = pd.to_datetime(df["posted_at"], errors="coerce")
    return df


def drop_nulls(df):
    return df.dropna()


def save_processed_data(df):
    processed_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_csv, index=False)
    print(f"Processed data saved to {processed_csv}")



def main():

    if not raw_csv.exists():
        print(f"File not found: {raw_csv}")
        return

    df = pd.read_csv(raw_csv)

    # Remove rows with null names
    df = drop_nullvalues_in_name(df)

    # Remove duplicates
    df = drop_duplicate_data(df)

    # Clean price column
    df = clean_price(df)

    # Normalize text, numeric, and date fields
    df = clean_text_columns(df)
    df = clean_numeric_columns(df)
    df = clean_posted_at(df)

    # Remove null values 
    df = drop_nulls(df)

    save_processed_data(df)


if __name__ == "__main__":
    main()
