import requests
import re
from agent.sql_generator import clean_sql, quote_columns_with_spaces

OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "llama3.2"

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL_NAME = "llama-3.3-70b-versatile"


def agent_loop_generate_and_run(
    question,
    schema,
    execute_func,
    validate_func,
    provider="ollama",
    api_key=None,
    max_retries=3,
):
    """Generate SQL, validate it, execute it, and retry with improved prompts on failure."""

    if not schema or not str(schema).strip():
        raise Exception("Schema is empty. Upload a CSV/Excel/SQLite file first.")

    prompt = f"""
You are a strict SQLite SQL generator for a READ-ONLY analytics system.

**CRITICAL CONSTRAINTS:**

This system is READ-ONLY. You MUST generate ONLY SELECT queries or CTE (WITH) queries that ultimately SELECT.

FORBIDDEN operations:
- INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, REPLACE, MERGE, EXEC, EXECUTE
- Transaction statements (BEGIN, COMMIT, ROLLBACK)
- PRAGMA modifications, VACUUM, ATTACH, DETACH
- Any data modification operations

If the user's question implies data modification (e.g., "delete", "remove", "update", "drop", "truncate", "create", "insert", "alter"), 
you MUST refuse and explain that only read-only analytical queries are supported.

DATABASE SCHEMA:
{schema}

QUESTION:
{question}

RULES:

1. Use ONLY tables listed in DATABASE SCHEMA.
2. Use ONLY columns listed in DATABASE SCHEMA.
3. NEVER invent tables.
4. NEVER invent columns.
5. Use ONLY tables and columns explicitly listed in the schema.

6. If only one table exists,
   DO NOT generate JOIN statements.

7. Generate ONLY SELECT or WITH...SELECT queries.

8. Do NOT generate any data modification statements.

9. Return ONLY SQL.

SQL:
"""

    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict SQL analyst for a READ-ONLY analytics system. "
                "Generate only SELECT queries or CTE (WITH) queries that ultimately SELECT. "
                "Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, or any data modification operations. "
                "If the user requests data modification, refuse and explain that only read-only analytical queries are allowed."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    last_error = None
    last_sql = ""

    print(f"\n🚀 [Agent Loop] Starting with Provider: {provider.upper()}")
    print(f"🚀 [Agent Loop] Max Retries: {max_retries}")

    for attempt in range(max_retries):
        current_attempt = attempt + 1
        print(f"\n🔄 [Agent Loop] Attempt {current_attempt}/{max_retries}...")
        raw_response = ""

        try:
            if provider == "groq":
                if not api_key:
                    raise Exception("Groq API key not provided")

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": GROQ_MODEL_NAME,
                    "messages": messages,
                    "temperature": 0.1,
                    "top_p": 0.9,
                }
                response = requests.post(
                    GROQ_URL, headers=headers, json=payload, timeout=30
                )
                if response.status_code != 200:
                    raise Exception(f"Groq API Error: {response.text}")
                raw_response = response.json()["choices"][0]["message"]["content"]
            else:
                # Format messages array to plain string for Ollama prompt
                ollama_prompt = "\n".join([m["content"] for m in messages])
                payload = {
                    "model": MODEL_NAME,
                    "prompt": ollama_prompt,
                    "stream": False,
                    "options": {"temperature": 0.1},
                }
                response = requests.post(
                    f"{OLLAMA_URL}/api/generate", json=payload, timeout=60
                )
                if response.status_code != 200:
                    raise Exception(f"Ollama returned {response.status_code}")
                raw_response = response.json().get("response", "")

            sql = clean_sql(raw_response)
            last_sql = sql

            # 1. Validate SQL
            print("⚙️ [Agent Loop] Validating generated SQL...")
            is_valid = validate_func(sql)
            if not is_valid:
                error_msg = (
                    f"The generated SQL '{sql}' is invalid. "
                    "It might contain restricted keywords. "
                    "Please generate a simple SELECT query."
                )
                print(f"❌ [Agent Loop] Validation Failed: {error_msg}")
                messages.append({"role": "assistant", "content": raw_response})
                messages.append({"role": "user", "content": error_msg})
                last_error = error_msg
                print("🔄 [Agent Loop] Triggering Retry...")
                continue

            # 2. Execute SQL
            print("⚙️ [Agent Loop] Validation Passed. Executing SQL...")
            sql = quote_columns_with_spaces(sql, schema)
            results_df = execute_func(sql)
            print(
                f"✅ [Agent Loop] SQL executed successfully on Attempt {current_attempt}!"
            )
            return sql, results_df

        except Exception as e:
            # If execution fails, tell the model the schema might not contain
            # referenced columns/tables and it must pick an alternative.
            error_msg = (
                f"Execution failed with error: {str(e)}. "
                "The dataset schema you uploaded may not contain the referenced table or column. "
                "Please correct the SQL using ONLY tables and columns that exist in the uploaded schema. "
                "If a requested field is missing, generate an alternative valid query that answers the question with available columns. "
                "Return ONLY the corrected SQL code."
            )

            # Optional auto-correction: underscore -> space for column names.
            if "no such column" in str(e).lower():
                corrected_sql = re.sub(
                    r"\b([A-Za-z0-9_]+)\b",
                    lambda m: f'"{m.group(1).replace("_", " ")}"'
                    if "_" in m.group(1)
                    else m.group(1),
                    last_sql,
                )
                try:
                    results_df = execute_func(corrected_sql)
                    return corrected_sql, results_df
                except Exception as inner_e:
                    error_msg = (
                        f"Execution failed after auto-correction: {str(inner_e)}. "
                        "Please generate a new valid SELECT query that uses existing columns only."
                    )

            print(f"❌ [Agent Loop] Execution Failed: {str(e)}")

            messages.append(
                {"role": "assistant", "content": raw_response if raw_response else last_sql}
            )
            messages.append({"role": "user", "content": error_msg})
            last_error = str(e)
            print("🔄 [Agent Loop] Triggering Retry...")

    print(f"🚨 [Agent Loop] All {max_retries} retries exhausted. Failing.")
    raise Exception(
        f"Agent Loop Failed after {max_retries} retries. Last Error: {last_error}\nLast SQL attempted: {last_sql}"
    )

