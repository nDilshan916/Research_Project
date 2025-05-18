import pandas as pd

def preprocess_data(df):
    """Preprocess the dataset."""
    df.dropna(inplace=True)
    df['Job title'] = df['Job title'].str.lower()
    return df

def clean_job_title(title):
    # Example: simple cleaning
    return title.strip().lower()