import streamlit as st
import pandas as pd
import os
import io
import re
import uuid
from datetime import datetime

from database.dynamic_db import (
    create_database_from_dataframe,
    get_schema,
    get_row_count,
    get_column_names,
    get_all_tables_metadata,
    get_table_data,
    get_table_schema,
    get_table_names,
)
from agent.sql_generator import (
    generate_sql,
    check_ollama_status
)
from agent.agent_loop import agent_loop_generate_and_run
from agent.validator import (
    validate_sql,
    validate_natural_language_intent,
    security_error_message
)
from agent.sql_executor import execute_sql
from agent.chart_generator import create_chart
from agent.explanation_generator import explain_sql

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="NL → SQL Analytics Agent",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------
st.markdown("""
<style>

/* ---------- FONT & BASE ---------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

:root {
    --brand: #8b5cf6;
    --brand-dark: #7c3aed;
    --brand-light: #a78bfa;
    --ink: #ffffff;
    --muted: #d1d5db;
    --line: #374151;
    --surface: #020617;
    --surface-alt: #111827;
}

html, body, .main .block-container, section[data-testid="stSidebar"] {
    background: #000000 !important;
    color: #ffffff !important;
}

.main .block-container {
    padding-top: 2.2rem;
    max-width: 1250px;
}

/* ---------- HEADINGS ---------- */
.main-title {
    text-align: center;
    font-size: 44px;
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(135deg, var(--brand) 0%, var(--brand-light) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 6px;
}

.sub-title {
    text-align: center;
    color: var(--muted);
    font-size: 16px;
    margin-bottom: 28px;
}

h2, h3 {
    color: var(--ink) !important;
    font-weight: 700 !important;
    letter-spacing: -0.3px;
}

/* ---------- BUTTONS ---------- */
div.stButton > button {
    background: linear-gradient(135deg, var(--brand) 0%, var(--brand-light) 100%);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    padding: 0.55rem 1.2rem;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.28);
    transition: all 0.18s ease;
}

div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.40);
    background: linear-gradient(135deg, var(--brand-dark) 0%, var(--brand) 100%);
}

div.stButton > button:active {
    transform: translateY(0);
}

/* ---------- INPUTS ---------- */
.stTextInput > div > div > input,
.stTextArea textarea,
.stSelectbox > div > div {
    border-radius: 10px !important;
    border: 1px solid var(--line) !important;
}

.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: var(--brand) !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12) !important;
}

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid #4338ca;
}

section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] .stSubheader,
section[data-testid="stSidebar"] .css-1v3fvcr,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] .stMarkdown {
    color: #ffffff;
}

section[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
    color: #ffffff;
    border: none;
}

section[data-testid="stSidebar"] .stFileUploader {
    background: #111827;
    border: 1px solid #374151;
    border-radius: 12px;
}

/* ---------- DATASET SUMMARY CARD ---------- */
.dataset-summary-card {
    background: #111827;
    color: #ffffff;
    padding: 22px 24px;
    border: 1px solid #374151;
    border-radius: 16px;
    margin-top: 12px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.35);
}

.dataset-summary-row {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    margin-bottom: 12px;
}

.dataset-summary-label {
    font-size: 13px;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.4px;
}

.dataset-summary-value {
    font-size: 18px;
    font-weight: 800;
    color: var(--brand);
}

.dataset-summary-fields { display: block; }

.dataset-summary-list {
    list-style: none;
    margin: 10px 0 0 0;
    padding: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.dataset-summary-list li {
    margin: 0;
}

.dataset-summary-field {
    display: inline-block;
    background: rgba(79, 70, 229, 0.08);
    color: var(--brand-dark);
    font-weight: 600;
    font-size: 13px;
    padding: 5px 12px;
    border-radius: 9999px;
    border: 1px solid rgba(79, 70, 229, 0.18);
}

/* ---------- SUMMARY / RESULT TABLES ---------- */
.summary-table {
    width: 100%;
    margin: 12px 0;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 14px rgba(0, 0, 0, 0.45);
    border: 1px solid #374151;
    background: #0f172a;
}

.summary-table th {
    background: #111827;
    color: #ffffff;
    text-align: left;
    padding: 12px 14px;
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}

.summary-table td {
    padding: 11px 14px;
    border-bottom: 1px solid #374151;
    color: #e5e7eb;
    font-size: 14px;
}

.summary-table tbody tr:last-child td { border-bottom: none; }
.summary-table tbody tr:nth-child(even) { background: var(--surface-alt); }
.summary-table tbody tr:hover { background: rgba(79, 70, 229, 0.05); }

/* ---------- CODE BLOCKS ---------- */
.stCodeBlock, pre {
    border-radius: 12px !important;
    border: 1px solid var(--line);
}

/* ---------- ALERTS ---------- */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
}

/* ---------- EXPANDER ---------- */
.streamlit-expanderHeader, [data-testid="stExpander"] details summary {
    border-radius: 10px !important;
    font-weight: 600;
}

/* ---------- SCROLLBAR ---------- */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: var(--surface-alt); }
::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 9999px;
    border: 2px solid var(--surface-alt);
}
::-webkit-scrollbar-thumb:hover { background: var(--brand-light); }

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "dataset_loaded" not in st.session_state:
    st.session_state.dataset_loaded = False
if "database_path" not in st.session_state:
    st.session_state.database_path = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = ""
if "schema" not in st.session_state:
    st.session_state.schema = ""
if "question" not in st.session_state:
    st.session_state.question = ""
if "selected_table_preview" not in st.session_state:
    st.session_state.selected_table_preview = None
if "query_executed" not in st.session_state:
    st.session_state.query_executed = False

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown(
    '<div class="main-title">NL → SQL Analytics Agent</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-title">Upload CSV, Excel, or a SQLite database file and ask questions in plain English</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.markdown("### 👋 Welcome\n\nUpload your dataset and ask questions in plain English.")

st.sidebar.subheader("🤖 LLM Provider")
provider_choice = st.sidebar.radio(
    "Select Provider",
    ["Local (Ollama)", "External (Groq API)"],
    index=0
)

api_key = None

if provider_choice == "External (Groq API)":
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        st.sidebar.success("Groq Connected")
    else:
        st.sidebar.error("⚠️ Groq API Key Missing! Please add GROQ_API_KEY to your .env file.")
else:
    st.sidebar.subheader("⚙️ System Status")
    ollama_running, has_model, models = check_ollama_status()
    if ollama_running and has_model:
        st.sidebar.success("Ollama Connected")
    else:
        st.sidebar.error("Ollama Not Available")

# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
st.sidebar.subheader("📂 Upload Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload Dataset File",
    type=["csv", "xlsx", "xls", "db", "sqlite", "sqlite3"],
    label_visibility="collapsed",
)


def _new_database_path() -> str:
    os.makedirs("database", exist_ok=True)
    return os.path.join("database", f"uploaded_data_{uuid.uuid4().hex[:8]}.db")


def _sanitize_table_name(filename: str) -> str:
    table_name = os.path.splitext(filename)[0]
    table_name = re.sub(r"[^0-9a-zA-Z_]", "_", table_name)
    if not table_name:
        table_name = "uploaded_data"
    if table_name[0].isdigit():
        table_name = f"t_{table_name}"
    return table_name


if uploaded_file and uploaded_file.name != st.session_state.uploaded_file_name:
    try:
        filename = uploaded_file.name.lower()
        db_path = _new_database_path()

        previous_path = st.session_state.get("database_path")
        if previous_path and previous_path != db_path and os.path.exists(previous_path):
            try:
                os.remove(previous_path)
            except Exception:
                pass

        st.session_state.database_path = db_path
        st.session_state.uploaded_file_name = uploaded_file.name
        st.session_state.selected_table_preview = None
        st.session_state.executed_sql = ""
        st.session_state.results_df = None
        st.session_state.query_executed = False

        if filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            table_name = _sanitize_table_name(uploaded_file.name)
            create_database_from_dataframe(df, db_path=db_path, table_name=table_name)
            st.session_state.active_table_name = table_name

        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
            table_name = _sanitize_table_name(uploaded_file.name)
            create_database_from_dataframe(df, db_path=db_path, table_name=table_name)
            st.session_state.active_table_name = table_name

        elif filename.endswith((".db", ".sqlite", ".sqlite3")):
            with open(db_path, "wb") as db_file:
                db_file.write(uploaded_file.getbuffer())
            st.sidebar.success("SQLite database uploaded")
            actual_tables = get_table_names(db_path=db_path)
            if not actual_tables:
                raise ValueError("Uploaded SQLite database contains no tables.")
            st.session_state.active_table_name = actual_tables[0]

        else:
            raise ValueError("Unsupported file type. Please upload CSV, Excel, or SQLite database files.")

        st.session_state.dataset_loaded = True
        st.session_state.schema = get_schema(st.session_state.database_path)

    except Exception as e:
        st.error(f"Dataset Upload Failed: {str(e)}")
        st.stop()

# --------------------------------------------------
# STOP IF NO DATASET
# --------------------------------------------------
if not st.session_state.dataset_loaded:
    st.info("Please upload a CSV or Excel dataset to begin.")
    st.stop()

# --------------------------------------------------
# DATASET SUMMARY
# --------------------------------------------------
st.subheader("Dataset Summary")
st.markdown(
    "This dataset has been uploaded successfully. Use the fields below when asking questions in plain English."
)

# Check if we have a table preview open
if st.session_state.selected_table_preview:
    # Display table schema and preview
    col1, col2 = st.columns([1, 0.15], gap="large")
    with col1:
        st.markdown(f"**Table: {st.session_state.selected_table_preview}**")
    with col2:
        if st.button("Close", key="close_preview", use_container_width=True):
            st.session_state.selected_table_preview = None
            st.rerun()

    available_tables = get_table_names(db_path=st.session_state.database_path)
    if st.session_state.selected_table_preview not in available_tables:
        st.warning("The selected table is not available in the uploaded database.")
    else:
        # Display schema information
        table_schema = get_table_schema(
            st.session_state.selected_table_preview,
            db_path=st.session_state.database_path,
        )
        if table_schema:
            with st.expander("📋 Column Schema", expanded=True):
                schema_text = "\n".join([f"{col_name} ({col_type})" for col_name, col_type in table_schema])
                st.code(schema_text, language="text")

        # Display data preview
        st.markdown("**Preview** (Scrollable)")
        preview_data = get_table_data(
            st.session_state.selected_table_preview,
            limit=50,
            db_path=st.session_state.database_path,
        )
        if preview_data.empty:
            st.info("No data available in this table.")
        else:
            st.dataframe(preview_data, use_container_width=True, height=400)

else:
    # Display multi-table summary
    tables_metadata = get_all_tables_metadata(
        db_path=st.session_state.database_path
    )

    if tables_metadata:
        # Create rows for each table
        for idx, table_meta in enumerate(tables_metadata):
            col1, col2, col3, col4, col5 = st.columns([2, 1.2, 1.2, 1, 1.2], gap="small")

            with col1:
                st.markdown(f"**Table:** `{table_meta['table_name']}`")
            with col2:
                st.markdown(f"<div class='dataset-summary-label'>Rows</div><div class='dataset-summary-value'>{table_meta['row_count']}</div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='dataset-summary-label'>Columns</div><div class='dataset-summary-value'>{table_meta['column_count']}</div>", unsafe_allow_html=True)
            with col4:
                st.write("")  # Spacer
            with col5:
                if st.button("View", key=f"view_btn_{idx}", use_container_width=True):
                    st.session_state.selected_table_preview = table_meta['table_name']
                    st.rerun()

    else:
        # Fallback for single table uploads
        table_names = get_table_names(db_path=st.session_state.database_path)
        active_table = st.session_state.get("active_table_name") or (table_names[0] if table_names else "uploaded_data")
        columns = get_column_names(db_path=st.session_state.database_path)
        row_count = get_row_count(db_path=st.session_state.database_path)
        column_count = len(columns)

        summary_html = f"""
        <div class="dataset-summary-card">
            <div class="dataset-summary-row">
                <span class="dataset-summary-label">Rows:</span>
                <span class="dataset-summary-value">{row_count}</span>
                <span class="dataset-summary-label">Columns:</span>
                <span class="dataset-summary-value">{column_count}</span>
                <span class="dataset-summary-label">Table:</span>
                <span class="dataset-summary-value">{active_table}</span>
            </div>
            <div class="dataset-summary-row dataset-summary-fields">
                <span class="dataset-summary-label">Fields:</span>
                <ul class="dataset-summary-list">
                    {''.join([f'<li><span class="dataset-summary-field">{col}</span></li>' for col in columns])}
                </ul>
            </div>
        </div>
        """
        st.markdown(summary_html, unsafe_allow_html=True)

# --------------------------------------------------
# QUESTION INPUT
# --------------------------------------------------
st.subheader("Ask Your Question")

question = st.text_input(
    "Enter your question",
    value="",
    placeholder="Example: Average salary by department"
)

generate_button = st.button("Generate SQL & Analyze", use_container_width=True)

# --------------------------------------------------
# RUN ANALYSIS
# --------------------------------------------------
if generate_button:
    if not question.strip():
        st.warning("Please enter a question.")
        st.stop()

    # LAYER 1: Natural Language Validation
    # Check for destructive intent BEFORE calling LLM
    is_safe, nl_message = validate_natural_language_intent(question)
    if not is_safe:
        st.error(nl_message)
        st.stop()

    schema = st.session_state.schema
    provider_val = "groq" if provider_choice == "External (Groq API)" else "ollama"

    if provider_val == "groq" and not api_key:
        st.error("Please provide a Groq API Key in the sidebar.")
        st.stop()

    if provider_val == "ollama":
        running, has_mod, _ = check_ollama_status()
        if not running or not has_mod:
            st.error("Ollama is not running or the required model is missing.")
            st.stop()

    with st.spinner(f"Agent Loop: Generating and verifying SQL via {provider_choice}..."):
        try:
            sql_to_run, results_df = agent_loop_generate_and_run(
                question=question,
                schema=schema,
                execute_func=lambda sql: execute_sql(sql, db_path=st.session_state.database_path),
                validate_func=validate_sql,
                provider=provider_val,
                api_key=api_key,
                max_retries=3
            )
            st.session_state.executed_sql = sql_to_run
            st.session_state.results_df = results_df
            st.session_state.question = question
            st.session_state.query_executed = True
        except Exception as e:
            st.error(f"Agent Loop Failed: {str(e)}")
            st.session_state.query_executed = False
            st.stop()

    st.subheader("Executed SQL Query")
    st.code(st.session_state.executed_sql, language="sql", line_numbers=True)

# --------------------------------------------------
# EXECUTE QUERY / MANUAL EDITOR
# --------------------------------------------------
if st.session_state.get("query_executed", False):
    with st.expander("🛠️ Manual SQL Editor"):
        manual_sql = st.text_area(
            "Edit or enter SQL manually:",
            value=st.session_state.get('executed_sql', ''),
            height=200,
        )
        if st.button("Run Manual SQL"):
            # LAYER 4: Execution Safety - Validate before executing manual SQL
            if not validate_sql(manual_sql):
                st.error(security_error_message())
                st.stop()
            
            try:
                manual_results_df = execute_sql(manual_sql, db_path=st.session_state.database_path)
                st.success("Manual SQL executed successfully.")
                st.session_state.results_df = manual_results_df
                st.session_state.executed_sql = manual_sql
                st.session_state.query_executed = True
            except Exception as e:
                st.error(f"Manual execution failed: {str(e)}")

    sql_query = st.session_state.executed_sql
    results_df = st.session_state.results_df

    st.markdown(
        "<h3>Query Execution &nbsp; <span style='color:#16a34a; font-weight:700;'>✅ Success</span></h3>",
        unsafe_allow_html=True
    )

    # ---------- EXPLANATION ----------
    st.subheader("Business Explanation")
    try:
        provider_val = "groq" if provider_choice == "External (Groq API)" else "ollama"
        explanation = explain_sql(sql_query, provider=provider_val, api_key=api_key)
        st.markdown(explanation)
    except Exception:
        st.markdown("Explanation could not be generated.")
        explanation = ""

    # ---------- RESULT METRICS + RESULTS ----------
    if results_df is None or results_df.empty:
        st.info("No results returned.")
    else:
        left_col, right_col = st.columns([1, 1], gap="small")

        with left_col:
            st.subheader("Result Summary")
            numeric_count = len(results_df.select_dtypes(include="number").columns)
            summary_df = pd.DataFrame(
                {
                    "Metric": ["Rows Returned", "Columns Returned", "Numeric Fields"],
                    "Value": [len(results_df), len(results_df.columns), numeric_count],
                }
            )
            st.dataframe(summary_df, use_container_width=True, height=140)

        with right_col:
            st.subheader("Query Results")
            if results_df.empty:
                st.warning("No records returned.")
            else:
                # Fixed-height scrollable display (approx. 5 visible rows)
                visible_height = 260
            st.dataframe(results_df, use_container_width=True, height=visible_height)

            # Export helpers (use current results; no re-execution)
            def _generate_excel_bytes(df: pd.DataFrame, question: str, sql: str, timestamp: str) -> bytes:
                try:
                    # existence check for openpyxl
                    import openpyxl  # type: ignore
                except Exception:
                    raise ImportError("openpyxl is required for Excel export. Install with: pip install openpyxl")

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df.to_excel(writer, sheet_name="Results", index=False)

                buffer.seek(0)
                return buffer.read()

            def _generate_pdf_bytes(df: pd.DataFrame, question: str, sql: str, timestamp: str, summary: dict) -> bytes:
                try:
                    from reportlab.lib.pagesizes import letter, landscape
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
                    from reportlab.lib.styles import getSampleStyleSheet
                    from reportlab.lib import colors
                except Exception:
                    raise ImportError("reportlab is required for PDF export. Install with: pip install reportlab")

                buf = io.BytesIO()
                pagesize = letter
                if len(df.columns) > 6:
                    pagesize = landscape(letter)

                doc = SimpleDocTemplate(buf, pagesize=pagesize, leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)
                styles = getSampleStyleSheet()
                elems = []
                elems.append(Paragraph("NL → SQL Analytics Report", styles["Title"]))
                elems.append(Spacer(1, 12))
                elems.append(Paragraph("<b>User Question</b>", styles["Heading2"]))
                elems.append(Paragraph(question, styles["Normal"]))
                elems.append(Spacer(1, 8))
                elems.append(Paragraph("<b>Generated SQL Query</b>", styles["Heading2"]))
                elems.append(Paragraph(sql, styles["Normal"]))
                elems.append(Spacer(1, 8))
                elems.append(Paragraph("<b>Execution Timestamp</b>", styles["Heading2"]))
                elems.append(Paragraph(timestamp, styles["Normal"]))
                elems.append(Spacer(1, 12))
                elems.append(Paragraph("<b>Result Summary</b>", styles["Heading2"]))

                summary_data = [["Metric", "Value"], ["Rows Returned", summary.get("rows")], ["Columns Returned", summary.get("columns")], ["Numeric Fields", summary.get("numeric")]]
                tbl = Table(summary_data, hAlign="LEFT", colWidths=[150, 100])
                tbl.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                elems.append(tbl)
                elems.append(Spacer(1, 12))
                elems.append(Paragraph("<b>Query Results</b>", styles["Heading2"]))

                data = [list(df.columns)] + df.values.tolist()
                for r_idx, row in enumerate(data):
                    for c_idx, cell in enumerate(row):
                        if cell is None:
                            data[r_idx][c_idx] = ""
                        elif not isinstance(cell, (str, bytes)):
                            try:
                                data[r_idx][c_idx] = str(cell)
                            except Exception:
                                data[r_idx][c_idx] = ""

                col_width = max(60, int((pagesize[0] - 48) / max(1, len(df.columns))))
                table = Table(data, repeatRows=1, colWidths=[col_width] * len(df.columns))
                table.setStyle(TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8f8f8")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                elems.append(table)
                doc.build(elems)
                buf.seek(0)
                return buf.read()

            question_text = st.session_state.get("question", "")
            sql_text = st.session_state.get("executed_sql", "")
            exec_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

            summary = {
                "rows": len(results_df),
                "columns": len(results_df.columns),
                "numeric": len(results_df.select_dtypes(include="number").columns)
            }

            btn_col1, btn_col2 = st.columns([3, 1], gap="small")
            with btn_col1:
                if st.button("Export Excel"):
                    try:
                        excel_bytes = _generate_excel_bytes(results_df, question_text, sql_text, exec_time)
                        st.success("Excel file generated. Click to download.")
                        st.download_button(
                            label="Download Excel",
                            data=excel_bytes,
                            file_name=f"nl_sql_report_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except ImportError as ie:
                        st.error(str(ie))
                    except Exception as e:
                        st.error(f"Excel export failed: {str(e)}")

            with btn_col2:
                if st.button("Export PDF"):
                    try:
                        pdf_bytes = _generate_pdf_bytes(results_df, question_text, sql_text, exec_time, summary)
                        st.success("PDF report generated. Click to download.")
                        st.download_button(
                            label="Download PDF",
                            data=pdf_bytes,
                            file_name=f"nl_sql_report_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.pdf",
                            mime="application/pdf"
                        )
                    except ImportError as ie:
                        st.error(str(ie))
                    except Exception as e:
                        st.error(f"PDF export failed: {str(e)}")

# --------------------------------------------------
# CHARTS
# --------------------------------------------------
if st.session_state.get("query_executed", False):
    results_df = st.session_state.results_df

    if results_df is not None and not results_df.empty:
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2.5, 1.2, 6], gap="small", vertical_alignment="center")
        with col1:
            st.subheader("Visualization")
        with col2:
            chart_type = st.selectbox(
                "Chart Type",
                ["No Chart", "Bar", "Line", "Pie", "Scatter", "Auto"],
                index=1,
                key="chart_type_selector",
                label_visibility="collapsed"
            )

        try:
            if chart_type == "No Chart":
                fig = None
            elif chart_type == "Auto":
                fig = create_chart(results_df, st.session_state.question)
            else:
                import plotly.express as px
                numeric_cols = results_df.select_dtypes(include="number").columns.tolist()
                categorical_cols = results_df.select_dtypes(include="object").columns.tolist()

                if not numeric_cols:
                    fig = None
                else:
                    x_col = categorical_cols[0] if categorical_cols else numeric_cols[0]
                    y_col = numeric_cols[0]

                    if chart_type == "Bar":
                        fig = px.bar(results_df, x=x_col, y=y_col, color=x_col, title=st.session_state.question)
                    elif chart_type == "Line":
                        fig = px.line(results_df, x=x_col, y=y_col, title=st.session_state.question, markers=True)
                        fig.update_traces(line_shape="spline", line=dict(width=3), marker=dict(size=8))
                    elif chart_type == "Pie":
                        fig = px.pie(results_df, names=x_col, values=y_col, title=st.session_state.question)
                    elif chart_type == "Scatter":
                        fig = px.scatter(results_df, x=x_col, y=y_col, color=x_col if categorical_cols else None, title=st.session_state.question)
                        fig.update_traces(marker=dict(size=12, line=dict(width=1, color='White')), opacity=0.8)
                    else:
                        fig = create_chart(results_df, st.session_state.question)

            if fig is not None and chart_type != "No Chart":
                fig.update_layout(
                    font=dict(family="Inter, sans-serif", color="#ffffff"),
                    title_font=dict(size=18, color="#ffffff"),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#ffffff",
                    margin=dict(t=60, l=20, r=20, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
            elif chart_type != "No Chart":
                st.info("No suitable chart could be generated.")

        except Exception as e:
            st.warning(f"Chart generation failed: {str(e)}")
