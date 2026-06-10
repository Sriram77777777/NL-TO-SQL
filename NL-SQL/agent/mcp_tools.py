from mcp.server.fastmcp import FastMCP
import sqlite3
import pandas as pd
import os

DEFAULT_DB_PATH = os.getenv("NL_SQL_DATABASE_PATH", "database/uploaded_data.db")

# Create an MCP server to expose tools
mcp = FastMCP("NL_TO_SQL_MCP")

def get_schema(db_path: str = DEFAULT_DB_PATH) -> str:
    """Helper to get DB schema"""
    if not os.path.exists(db_path):
        return "No database uploaded yet."
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    
    if not tables:
        return "Database is empty."
        
    return "\n\n".join([table[0] for table in tables if table[0]])

@mcp.tool()
def get_database_schema() -> str:
    """
    Returns the schema of the uploaded database.
    This exposes our database dynamically to external MCP clients.
    """
    try:
        schema = get_schema()
        return f"Current Database Schema:\n{schema}"
    except Exception as e:
        return f"Error retrieving schema: {str(e)}"

@mcp.tool()
def run_sql_query(query: str, db_path: str = DEFAULT_DB_PATH) -> str:
    """
    Executes a SQL query on the uploaded database and returns the result as text.
    """
    try:
        if not os.path.exists(db_path):
            return "No database uploaded yet."
            
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df.to_string(index=False)
    except Exception as e:
        return f"Error executing query: {str(e)}"

if __name__ == "__main__":
    # Start the MCP server
    print("Starting NL to SQL MCP Server...")
    mcp.run()
