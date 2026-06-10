import sqlite3
import pandas as pd
import os

DEFAULT_DB_PATH = "database/uploaded_data.db"


def execute_sql(sql: str, db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Execute SQL query and return results as DataFrame.

    Parameters:
        sql (str): Valid SQL query
        db_path (str): SQLite database path

    Returns:
        pd.DataFrame
    """

    if not os.path.exists(db_path):
        raise FileNotFoundError(
            f"Database not found: {db_path}"
        )

    conn = None

    try:

        conn = sqlite3.connect(db_path)

        df = pd.read_sql_query(
            sql,
            conn
        )

        return df

    except Exception as e:

        raise Exception(
            f"SQL Execution Error: {str(e)}"
        )

    finally:

        if conn:
            conn.close()


def get_table_preview(
    limit: int = 10,
    db_path: str = DEFAULT_DB_PATH,
    table_name: str = "uploaded_data",
):
    """
    Preview uploaded dataset.
    """

    query = f"""
    SELECT *
    FROM {table_name}
    LIMIT {limit}
    """

    return execute_sql(query, db_path=db_path)


def get_total_rows(
    db_path: str = DEFAULT_DB_PATH,
    table_name: str = "uploaded_data",
):
    """
    Get total rows in uploaded table.
    """

    conn = None

    try:

        conn = sqlite3.connect(db_path)

        cursor = conn.cursor()

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM {table_name}
            """
        )

        count = cursor.fetchone()[0]

        return count

    finally:

        if conn:
            conn.close()


def get_column_names(
    db_path: str = DEFAULT_DB_PATH,
    table_name: str = "uploaded_data",
):
    """
    Get all column names.
    """

    conn = None

    try:

        conn = sqlite3.connect(db_path)

        cursor = conn.cursor()

        cursor.execute(
            f"""
            PRAGMA table_info({table_name})
            """
        )

        columns = cursor.fetchall()

        return [
            col[1]
            for col in columns
        ]

    finally:

        if conn:
            conn.close()


def get_table_info(
    db_path: str = DEFAULT_DB_PATH,
    table_name: str = "uploaded_data",
):
    """
    Return schema information.
    """

    conn = None

    try:

        conn = sqlite3.connect(db_path)

        cursor = conn.cursor()

        cursor.execute(
            f"""
            PRAGMA table_info({table_name})
            """
        )

        columns = cursor.fetchall()

        schema = []

        for col in columns:

            schema.append(
                {
                    "column_name": col[1],
                    "data_type": col[2],
                }
            )

        return pd.DataFrame(schema)

    finally:

        if conn:
            conn.close()


if __name__ == "__main__":

    try:

        print("\nRows in Dataset:")
        print(get_total_rows())

        print("\nColumns:")
        print(get_column_names())

        print("\nSchema:")
        print(get_table_info())

        print("\nPreview:")
        print(get_table_preview())

        query = """
        SELECT *
        FROM uploaded_data
        LIMIT 5
        """

        result = execute_sql(query)

        print("\nQuery Result:")
        print(result)

    except Exception as e:

        print(f"Error: {e}")