import pandas as pd
import sqlite3

def create_dynamic_database(csv_path, db_path):

    df = pd.read_csv(csv_path)

    # Clean column names
    df.columns = [
        col.strip()
           .lower()
           .replace(" ", "_")
           .replace("-", "_")
           .replace("/", "_")
        for col in df.columns
    ]

    conn = sqlite3.connect(db_path)

    df.to_sql(
        "uploaded_data",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    return df.columns.tolist()