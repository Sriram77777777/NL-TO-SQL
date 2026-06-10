import requests
import re

OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "llama3.2"

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL_NAME = "llama-3.3-70b-versatile"


def fallback_explanation(sql: str):
    """
    Basic fallback explanation when LLM providers are unavailable.
    """
    sql_lower = sql.lower()

    if "group by" in sql_lower:
        return (
            "This query groups the dataset and "
            "calculates summary statistics for each group."
        )

    if "avg(" in sql_lower:
        return (
            "This query calculates an average value "
            "from the uploaded dataset."
        )

    if "sum(" in sql_lower:
        return (
            "This query calculates total values "
            "from the uploaded dataset."
        )

    if "count(" in sql_lower:
        return (
            "This query counts records in the uploaded dataset."
        )

    return (
        "This query retrieves information from "
        "the uploaded dataset."
    )


def clean_response(text: str):
    """
    Clean model output.
    """
    if not text:
        return ""

    text = text.replace("```", "")
    text = text.replace("sql", "")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def explain_sql(sql: str, provider="ollama", api_key=None):
    """
    Generate business explanation for SQL query using either Ollama or Groq.
    """
    prompt = f"""
You are a senior business analyst.

Explain the SQL query in plain English.

Rules:
1. Maximum 2 sentences.
2. Business-friendly language.
3. Do not mention SQL syntax.
4. Do not mention SELECT, GROUP BY, ORDER BY.
5. Explain what insight the user receives.
6. Keep explanation short and clear.

SQL Query:
{sql}

Explanation:
"""

    if provider == "groq":
        if not api_key:
            return fallback_explanation(sql)
            
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": GROQ_MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        try:
            response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
            if response.status_code != 200:
                return fallback_explanation(sql)
            
            explanation = response.json()["choices"][0]["message"]["content"].strip()
            explanation = clean_response(explanation)
            
            return explanation if explanation else fallback_explanation(sql)
        except Exception:
            return fallback_explanation(sql)
            
    else:
        # Default to Ollama
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                return fallback_explanation(sql)

            explanation = response.json().get("response", "").strip()
            explanation = clean_response(explanation)

            return explanation if explanation else fallback_explanation(sql)

        except Exception:
            return fallback_explanation(sql)


if __name__ == "__main__":
    sample_sql = """
    SELECT department,
           AVG(salary)
    FROM uploaded_data
    GROUP BY department
    """
    
    print("Testing with local Ollama setup:")
    print(explain_sql(sample_sql, provider="ollama"))
