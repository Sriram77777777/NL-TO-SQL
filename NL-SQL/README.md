
# NL → SQL Analytics Agent

A Streamlit analytics assistant that converts your plain-English questions into **safe, read-only SQLite (SELECT) queries** over your uploaded dataset.

It validates the generated SQL, executes it on SQLite, explains the result, and visualizes it with Plotly.

# Team 26 - Team Members

| Name       | Resume |
|------------|--------|
| Sridharan C | [Resume](https://drive.google.com/file/d/1FsqizgchbN_-73A9V6yPBhQreOPBwpUN/view?usp=sharing) |
| Sriram N   | [Resume](https://drive.google.com/drive/u/0/folders/1V8Tf_3PZyQ0Hsf8bBuMQUSzmzv4wgu_G) |
| Srivignesh | [Resume](https://drive.google.com/file/d/1-N6MOkGysS2qRopJ5hQr5CmTLSjQbEkX/view?usp=sharing)|
| Suganth ST | [Resume](https://drive.google.com/file/d/1GlhLYtRdVSE9zurK_ghuQYb2QQwn3nBa/view?usp=drivesdk)


---
# Watch the project demonstration here:
## Demo Video
https://www.loom.com/share/215ad71c7b4a47fb821a74b06da7763d

<!-- [Demo Video](https://www.loom.com/share/215ad71c7b4a47fb821a74b06da7763d) -->

[TEST_CASES](https://drive.google.com/file/d/1VN-3022g7z472LWMhexhhLpSEvWr-SNS/view?usp=sharing)

[SAMPLE_DATA](https://drive.google.com/file/d/1G6eOmasd9YvDk9NlTGZQVVxxtEEa_5K7/view?usp=sharing)

[AI_Usage_Note](https://drive.google.com/file/d/1TgNQUC9i-VOHdUleyI0fE7nAzE69V-9K/view?usp=sharing)

# What the app does

Instead of writing SQL manually, upload a dataset and ask questions in plain English. The app:

1. Discovers your SQLite schema
2. Generates a **SELECT-only** SQL query (via Ollama or Groq)
3. Validates safety (blocks destructive SQL + stacked statements)
4. Executes the query on your uploaded data
5. Shows the results table + charts + explanation

# NL-To-SQL Analytics Agent

## DE-01: Schema-Grounded Text-to-SQL Agent

An AI-powered analytics platform that enables business users to query SQLite databases and datasets using natural language.

Instead of writing SQL manually, users can upload a dataset, ask questions in plain English, generate SQL automatically using AI, edit queries manually if required, and visualize results through interactive charts.


The platform supports both local and cloud LLM providers through a provider-selection interface.

---

# Key Features

## Dataset & Database Analysis

* Upload SQLite databases
* Automatic schema discovery
* Dataset summary generation
* Major column identification
* Row and column statistics
* Data preview

## AI-Powered SQL Generation

* Natural Language → SQL conversion
* Schema-aware prompting
* Ollama (Llama 3.2) integration
* Groq API integration
* Provider switching from sidebar
* SQL explanation generation

## Agent Loop

* Automated SQL generation
* Query validation
* Query execution
* Error detection
* Retry mechanism
* Detailed execution logging

## Manual SQL Editor

* Edit generated SQL before execution
* Re-run modified queries
* Compare AI-generated and manual queries

## Analytics & Insights

* Business insight generation
* Query result summaries
* Row count reporting
* Column count reporting
* Numeric column detection

## Interactive Visualizations

* Bar Charts
* Line Charts
* Pie Charts
* Scatter Charts
* Dynamic chart selection


## Security Features

* Read-only execution model
* SQL validation
* Dangerous query blocking
* SQL injection protection
* Multi-statement query blocking

---

# Architecture Flow
![alt text](architecture.png)
```text

```

---

# Technology Stack

| Component       | Technology               |
| --------------- | ------------------------ |
| Frontend        | Streamlit                |
| Backend         | Python 3.10+             |
| Database        | SQLite                   |
| AI Providers    | Ollama (Llama 3.2), Groq |
| Visualization   | Plotly                   |
| Agent Framework | Custom Agent Loop        |
| MCP Integration | Model Context Protocol   |
| Testing         | Pytest                   |

---

# Project Structure

```text
NL-TO-SQL-AGENT-main/
│
├── .gitignore
├── AI_Usage_Note.md
├── README.md
├── requirements.txt
├── retail_sales.css
├── TEST_CASES.md
│
├── app.py
├── create_db.py
├── .env
│
├── agent/
│   ├── agent_loop.py
│   ├── mcp_tools.py
│   ├── chart_generator.py
│   ├── explanation_generator.py
│   ├── insight_generator.py
│   ├── report_generator.py
│   ├── schema_tool.py
│   ├── sql_executor.py
│   ├── sql_generator.py
│   └── validator.py
│
├── database/
│   ├── dynamic_db.py
│   ├── test_sales.db
│   └── uploaded_data.db
│
│
├── sample_data/
│   ├── analytics_poc (1).db
│   ├── ecommerce.csv
│   └── retail_sales_dataset.csv
│
└── tests/
    └── test_agent.py
```

---

# Running the Application

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Streamlit

```bash
streamlit run app.py
```

## Provider Selection

The sidebar allows switching between:

* Local (Ollama)
* External (Groq API)

Groq API keys are loaded securely through the `.env` file.

---

# MCP Integration

The project includes MCP tools for schema access and future AI tool integration.

Available MCP Tools:

* get_schema()
* Database metadata access

---

# Agent Loop

The custom agent loop:

1. Generates SQL
2. Validates SQL
3. Executes SQL
4. Detects failures
5. Retries automatically
6. Returns validated results

Execution logs are displayed in the terminal for debugging and transparency.

---
# Installation

## Clone Repository

```bash
git clone <repository-url>
cd NL-TO-SQL-AGENT-main
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

This key is automatically loaded when the Groq provider is selected from the sidebar.

## Database Setup

Generate the sample SQLite database:

```bash
python create_db.py
```

This creates:

```text
database/uploaded_data.db
```

using:

```text
sample_data/retail_sales_dataset.csv
```

---

# Running the Application

## Option 1 – Ollama Mode

Install Ollama:

```bash
ollama pull llama3.2
```

Run the application:

```bash
streamlit run app.py
```

Select:

```text
Local (Ollama)
```

from the sidebar provider selector.

---

## Option 2 – Groq Mode

Add your Groq API key to the `.env` file.

Run:

```bash
streamlit run app.py
```

Select:

```text
External (Groq API)
```

from the sidebar provider selector.

---

# Sample Questions

Try asking:

* Total revenue by product category
* Monthly sales trend
* Top selling product
* Revenue by region
* Revenue vs Quantity
* Average sales by category
* Top 5 products by revenue
* Customer count by region
* Sales by month
* Highest revenue generating category

---

# Running Tests

Execute all tests:

```bash
pytest tests/test_agent.py
```

Run with verbose output:

```bash
pytest tests/test_agent.py -v
```

Covered Components:

* Schema Extraction
* SQL Generation
* SQL Validation
* Query Execution
* Chart Generation
* Agent Loop
* Business Insights

Detailed test documentation:

```text
TEST_CASES.md
```

---

# Security Features

The application enforces a strict read-only execution model.

## Allowed Queries

* SELECT
* WITH (CTE)
* JOIN
* AVERAGE
* SUM

## Blocked Queries

* DROP
* DELETE
* UPDATE
* INSERT
* ALTER
* CREATE
* TRUNCATE
* REPLACE

## Additional Protection

* SQL injection prevention
* Multi-statement query blocking
* Query validation before execution
* Read-only database access
* Manual SQL validation before execution

---

# Assumptions & Limitations

## Assumptions

1. Uploaded datasets are valid and accessible.
2. Ollama is installed when using local mode.
3. Groq API key is configured when using Groq mode.
4. Users ask analytical questions related to the uploaded dataset.
5. Schema extraction completes successfully.

## Limitations

1. SQL quality depends on the selected LLM.
2. Very large datasets may increase execution time.
3. Complex multi-table joins may require manual query editing.
4. Internet connectivity is required when using Groq.
5. The system is designed for analytics and reporting only.
6. Database write operations are intentionally blocked.

---





