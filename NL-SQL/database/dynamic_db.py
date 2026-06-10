import sqlite3
import pandas as pd
import os


DEFAULT_DB_PATH = "database/uploaded_data.db"
DEFAULT_TABLE_NAME = "uploaded_data"


def create_database_from_dataframe(
    df: pd.DataFrame,
    db_path: str = DEFAULT_DB_PATH,
    table_name: str = DEFAULT_TABLE_NAME,
):
    """
    Creates SQLite database from uploaded dataframe.
    Existing table will be replaced.
    """

    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    conn = sqlite3.connect(db_path)

    try:
        df.to_sql(
            table_name,
            conn,
            if_exists="replace",
            index=False,
        )
        conn.commit()

    finally:
        conn.close()

    return db_path, table_name


def get_table_names(db_path: str = DEFAULT_DB_PATH):
    """
    Returns all non-system table names from the uploaded database.
    """

    if not os.path.exists(db_path):
        return []

    conn = sqlite3.connect(db_path)

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        tables = cursor.fetchall()
        return [row[0] for row in tables]

    finally:
        conn.close()


def _get_primary_table(db_path: str = DEFAULT_DB_PATH):
    """
    Returns the main table to summarize.
    """

    tables = get_table_names(db_path)
    if not tables:
        return None
    return DEFAULT_TABLE_NAME if DEFAULT_TABLE_NAME in tables else tables[0]


def get_schema(db_path: str = DEFAULT_DB_PATH):
    """
    Returns schema information for the uploaded database.
    """

    tables = get_table_names(db_path)

    if not tables:
        return ""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    schema_parts = []

    try:
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            schema = f"Table: {table}\nColumns:\n"
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                schema += f"- {col_name} ({col_type})\n"
            schema_parts.append(schema)

        return "\n".join(schema_parts)

    finally:
        conn.close()


def get_column_names(db_path: str = DEFAULT_DB_PATH):
    """
    Returns a list of column names for the active uploaded table.
    """

    if not os.path.exists(db_path):
        return []

    table = _get_primary_table(db_path)
    if not table:
        return []

    conn = sqlite3.connect(db_path)

    try:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        return [col[1] for col in columns]

    finally:
        conn.close()


def get_row_count(db_path: str = DEFAULT_DB_PATH):
    """
    Returns total row count for the primary uploaded table.
    """

    if not os.path.exists(db_path):
        return 0

    table = _get_primary_table(db_path)
    if not table:
        return 0

    conn = sqlite3.connect(db_path)

    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        return cursor.fetchone()[0]

    finally:
        conn.close()


def database_exists(db_path: str = DEFAULT_DB_PATH):
    return os.path.exists(db_path)


def get_all_tables_metadata(db_path: str = DEFAULT_DB_PATH):
    """
    Returns a list of dictionaries containing metadata for all tables.
    Each dict has: table_name, row_count, column_count
    """

    if not os.path.exists(db_path):
        return []

    tables = get_table_names(db_path)
    if not tables:
        return []

    conn = sqlite3.connect(db_path)
    metadata_list = []

    try:
        cursor = conn.cursor()

        for table in tables:
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]

            # Get column count
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            column_count = len(columns)

            metadata_list.append({
                "table_name": table,
                "row_count": row_count,
                "column_count": column_count
            })

        return metadata_list

    finally:
        conn.close()


def get_table_data(table_name: str, limit: int = None, db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Fetches data from a specific table with optional row limit.
    If limit is None, fetches all rows.
    """

    if not os.path.exists(db_path):
        return pd.DataFrame()

    tables = get_table_names(db_path)
    if table_name not in tables:
        return pd.DataFrame()

    conn = sqlite3.connect(db_path)

    try:
        if limit is None:
            query = f"SELECT * FROM {table_name}"
        else:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        return df

    finally:
        conn.close()


def get_table_schema(table_name: str, db_path: str = DEFAULT_DB_PATH) -> list:
    """
    Returns column schema for a specific table.
    Returns list of tuples: [(column_name, column_type), ...]
    """

    if not os.path.exists(db_path):
        return []

    tables = get_table_names(db_path)
    if table_name not in tables:
        return []

    conn = sqlite3.connect(db_path)

    try:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        return [(col[1], col[2]) for col in columns]

    finally:
        conn.close()


if __name__ == "__main__":

    sample_df = pd.DataFrame(
        {
            "Department": ["IT", "HR", "Sales"],
            "Salary": [50000, 45000, 60000]
        }
    )

    create_database_from_dataframe(sample_df)

    print(get_schema())
    print(get_column_names())
    print(get_row_count())