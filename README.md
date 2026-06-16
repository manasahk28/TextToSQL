---
title: TextToSQL Agent Dashboard
emoji: 🤖
colorFrom: indigo
colorTo: cyan
sdk: streamlit
sdk_version: 1.40.0
app_file: src/ui/app.py
pinned: false
---

# 🤖 Text-to-SQL Agent Dashboard

An interactive, premium dashboard demonstrating a state-of-the-art **Text-to-SQL Agent** equipped with real-time **Chain-of-Thought (CoT) self-correction**, live database validation, and interactive data analytics.

The application translates natural language questions into valid SQL, runs them against a relational database facade, and automatically reflects and remedies syntax or schema errors using advanced LLMs (Groq or AWS Bedrock).

---

## 🌟 Features

- **CoT Self-Reflection Loop**: When generated SQL query validation fails, the agent reflections on the database error message, constructs a remedy plan, and attempts self-correction dynamically up to the iteration limit.
- **State-Persisted Interactive Dashboard**: Restructured using Streamlit session state, ensuring that your query traces, dataframes, and visualizations persist even when changing Plotly chart configurations.
- **Interactive Data Analytics**: Automatically auto-detects fields to recommend visualizers (Bar, Line, Pie, or Scatter charts) powered by Plotly.
- **Custom Data Sources**: Supports uploading custom SQLite databases (`.db`/`.sqlite`) or `.csv` files alongside standard networking database presets.
- **LLM Configuration**: Allows selecting providers (Groq or AWS Bedrock) and models (Llama 3.1/3.3, Mixtral, Claude 3/3.5) directly from the sidebar.

---

## 📁 Project Structure

- **`run_dashboard.py`**: Entrypoint to launch the Streamlit dashboard.
- **`run_tests.py`**: Entrypoint to launch the CLI evaluation test suite.
- **`src/`**: Primary source files directory.
  - **`src/ui/app.py`**: Streamlit dashboard code (layout, visualizations, controller).
  - **`src/agent/reflection_tasks.py`**: Agent prompt generation and correction algorithms.
  - **`src/agent/apply_llm.py`**: API interfaces for Groq and Bedrock models.
  - **`src/database/rdbms_facade.py`**: Relational database facade managing validations and mock data.
  - **`src/database/dbtables_schemas.py`** & **`dbtables_rules.py`**: Schemas DDL statements and PostgreSQL database rules.
  - **`src/app_constants.py`**: Global configs and limits configuration.
- **`tests/`**: Contains testing data and runners.
  - **`tests/main.py`**: Core logic for running the CLI evaluations.
  - **`tests/example_cases.py`**: Pre-configured query evaluation cases.

---

## ⚙️ Installation & Setup

### 1. Environment Preparation
Ensure you have Python 3.9+ installed. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
Install packages listed in the requirements file:
```bash
pip install -r requirements.txt
```

### 3. API Key Configuration
Create a `.env` file in the root directory and supply your Groq API Key:
```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## 🚀 Running the Application

### Launch the Interactive Dashboard
You can run the interactive Streamlit dashboard in either of two ways:

1. **Option A: Run the wrapper script (Recommended)**
   ```bash
   python run_dashboard.py
   ```
2. **Option B: Run Streamlit directly**
   ```bash
   streamlit run src/ui/app.py
   ```

*(By default, the dashboard serves on [http://localhost:8501](http://localhost:8501))*

### Run Evaluation Test Cases (CLI)
To run the evaluation test suite via terminal:
```bash
python run_tests.py
```
