import os
import sqlite3

def get_schema(db_path="database/uploaded_data.db"):
    """
    Connects to the SQLite database and retrieves schema information for all user tables.
    Returns a formatted string representing the schema for prompt inclusion.
    """
    if not os.path.exists(db_path):
        if db_path == "database/uploaded_data.db":
            return ""
        raise FileNotFoundError(f"Database not found at path: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get list of all non-system tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]
        
        schema_info = []
        for table in tables:
            # Query column details for each table
            cursor.execute(f"PRAGMA table_info({table});")
            columns_info = cursor.fetchall()
            
            cols = []
            pk_cols = []
            for col in columns_info:
                # col matches: (cid, name, type, notnull, dflt_value, pk)
                col_name = col[1]
                col_type = col[2]
                is_pk = col[5]
                
                col_desc = f"{col_name} ({col_type})"
                if is_pk:
                    col_desc += " PRIMARY KEY"
                    pk_cols.append(col_name)
                cols.append(col_desc)
                
            table_schema = f"Table: {table}\nColumns:\n  - " + "\n  - ".join(cols)
            schema_info.append(table_schema)
            
        return "\n\n".join(schema_info)
    
    except Exception as e:
        print(f"Error fetching database schema: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    # Test execution
    try:
        schema = get_schema()
        print("Retrieved Schema:")
        print(schema)
    except Exception as ex:
        print(f"Failed to test schema reading: {ex}")
