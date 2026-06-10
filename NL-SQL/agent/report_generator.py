import pandas as pd
from datetime import datetime

def generate_report(question: str, sql: str, explanation: str, confidence: int, results_df: pd.DataFrame, insights: list[str]) -> str:
    """
    Generates a plain-text analytics report string for download.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "=" * 60,
        "       NL-to-SQL Analytics Agent — Query Report",
        "=" * 60,
        f"Generated On : {now}",
        "",
        "QUESTION",
        "-" * 60,
        question,
        "",
        "GENERATED SQL",
        "-" * 60,
        sql,
        "",
        "AI EXPLANATION",
        "-" * 60,
        explanation,
        "",
        f"CONFIDENCE SCORE: {confidence}%",
        "",
        "QUERY RESULTS",
        "-" * 60,
    ]

    if results_df is not None and not results_df.empty:
        lines.append(results_df.to_string(index=False))
    else:
        lines.append("No records returned.")

    if insights:
        lines += ["", "ADDITIONAL INSIGHTS", "-" * 60]
        for insight in insights:
            clean = insight.replace("**", "").replace("", "").replace("", "").replace("", "").replace("", "").replace("", "").strip()
            lines.append(f"• {clean}")

    lines += ["", "=" * 60, "End of Report", "=" * 60]
    return "\n".join(lines)
