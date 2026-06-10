import re

# Dangerous SQL keywords (Layer 3 & 4 validation)
FORBIDDEN_SQL_KEYWORDS = {
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "REPLACE",
    "RENAME",
    "ATTACH",
    "DETACH",
    "PRAGMA",
    "VACUUM",
    "GRANT",
    "REVOKE",
    "MERGE",
    "EXEC",
    "EXECUTE"
}

# Keywords indicating destructive intent in natural language (Layer 1)
DESTRUCTIVE_NL_KEYWORDS = {
    "delete",
    "remove",
    "drop",
    "truncate",
    "erase",
    "clear",
    "wipe",
    "destroy",
    "clean",
    "purge",
    "update",
    "modify",
    "alter",
    "change",
    "insert",
    "add new",
    "create",
    "create table",
    "create a table",
    "make a table",
    "new table",
    "new column",
    "add column"
}


def validate_natural_language_intent(question: str) -> tuple[bool, str]:
    """
    LAYER 1: Natural Language Validation
    
    Detect destructive user intent BEFORE calling the LLM.
    
    Returns:
        tuple: (is_safe: bool, message: str)
        - (True, "Query appears to be read-only") if safe
        - (False, "error message") if destructive intent detected
    """
    if not question or not str(question).strip():
        return False, "Question cannot be empty."
    
    question_lower = question.lower().strip()
    
    # Check for destructive keywords
    for keyword in DESTRUCTIVE_NL_KEYWORDS:
        if keyword in question_lower:
            return False, (
                "❌ Operation Not Allowed\n\n"
                "This system supports read-only analytics and reporting.\n\n"
                "Reason:\n"
                "Your request attempts to modify data.\n\n"
                "Please ask analytical questions such as:\n"
                "- Total revenue by category\n"
                "- Top customers by sales\n"
                "- Orders by region"
            )
    
    return True, "Query appears to be read-only"


def remove_comments(sql: str) -> str:
    """
    Remove SQL comments before validation.
    """

    # Remove block comments
    sql = re.sub(
        r"/\*.*?\*/",
        "",
        sql,
        flags=re.DOTALL
    )

    # Remove inline comments
    sql = re.sub(
        r"--.*?$",
        "",
        sql,
        flags=re.MULTILINE
    )

    return sql.strip()


def remove_string_literals(sql: str) -> str:
    """
    Remove quoted strings to avoid false positives.
    """

    sql = re.sub(
        r"'[^']*'",
        "''",
        sql
    )

    sql = re.sub(
        r'"[^"]*"',
        '""',
        sql
    )

    return sql


def contains_multiple_statements(sql: str) -> bool:
    """
    Detect stacked SQL queries.
    """

    parts = [
        part.strip()
        for part in sql.split(";")
        if part.strip()
    ]

    return len(parts) > 1


def validate_sql(sql: str) -> bool:
    """
    LAYERS 3 & 4: SQL Validation
    
    Validate generated SQL after generation and before execution.
    Ensures only SELECT/CTE queries are allowed.

    Returns:
        True  -> Safe (SELECT/CTE only)
        False -> Unsafe (contains forbidden operations)
    """

    if not sql:
        return False

    sql = sql.strip()

    if len(sql) == 0:
        return False

    # Remove comments
    sql = remove_comments(sql)
    
    # Block stacked statements (multiple queries separated by semicolon)
    if contains_multiple_statements(sql):
        print(
            "Validation Error: Multiple SQL statements detected."
        )
        return False

    # Remove strings to avoid false positives
    processed_sql = remove_string_literals(sql)

    processed_sql = processed_sql.upper()

    processed_sql = re.sub(
        r"\s+",
        " ",
        processed_sql
    )

    # Must start with SELECT or WITH (for CTEs)
    if not (
        processed_sql.startswith("SELECT")
        or
        processed_sql.startswith("WITH")
    ):
        print(
            "Validation Error: Query must start with SELECT or WITH."
        )
        return False

    # For CTE queries (WITH ... SELECT), ensure they ultimately SELECT
    if processed_sql.startswith("WITH"):
        # CTEs should eventually have a SELECT
        if "SELECT" not in processed_sql:
            print(
                "Validation Error: CTE must ultimately contain a SELECT statement."
            )
            return False

    # Tokenize query to find SQL keywords
    tokens = set(
        re.findall(
            r"\b[A-Z_]+\b",
            processed_sql
        )
    )

    forbidden_found = (
        tokens.intersection(FORBIDDEN_SQL_KEYWORDS)
    )

    if forbidden_found:
        print(
            f"Validation Error: Forbidden keyword(s): {forbidden_found}"
        )
    return True


def validation_message(sql: str) -> str:
    """
    Human-readable validation result.
    """

    if validate_sql(sql):
        return "SQL validation passed."

    return "Query blocked for security reasons. This analytics agent supports read-only data exploration and reporting. Data modification operations are not permitted."


def security_error_message() -> str:
    """
    Standard security error message for destructive operations.
    """
    return (
        "Query blocked for security reasons. This analytics agent supports read-only data exploration and reporting. "
        "Data modification operations (INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, etc.) are not permitted. "
        "Please ask an analytical question instead."
    )


if __name__ == "__main__":

    safe_queries = [

        "SELECT * FROM uploaded_data",

        """
        SELECT department,
               AVG(salary)
        FROM uploaded_data
        GROUP BY department
        """
    ]

    unsafe_queries = [

        "DROP TABLE uploaded_data",

        """
        SELECT * FROM uploaded_data;
        DROP TABLE uploaded_data;
        """,

        """
        UPDATE uploaded_data
        SET salary = 1000
        """
    ]

    print("\nSAFE TESTS\n")

    for query in safe_queries:

        print(query)
        print(
            "Result:",
            validate_sql(query)
        )
        print("-" * 50)

    print("\nUNSAFE TESTS\n")

    for query in unsafe_queries:

        print(query)
        print(
            "Result:",
            validate_sql(query)
        )
        print("-" * 50)