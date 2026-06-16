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

- **[app.py](file:///d:/Projects/TextToSQL/app.py)**: The main Streamlit dashboard interface containing layout configuration, session-state management, visualizer rendering, and the agent evaluation controller.
- **[main.py](file:///d:/Projects/TextToSQL/main.py)**: Command-line runner to execute preset query test cases sequentially and print detailed CoT self-reflection traces.
- **[rdbms_facade.py](file:///d:/Projects/TextToSQL/rdbms_facade.py)**: Wraps SQLite to mock a PostgreSQL database structure, manage schemas, validate queries, and populate mock data (access policies, rules, intrusion logs, VPN entries).
- **[reflection_tasks.py](file:///d:/Projects/TextToSQL/reflection_tasks.py)**: Manages prompt engineering, LLM inference invocations, and parses thoughts/SQL outputs from models.
- **[apply_llm.py](file:///d:/Projects/TextToSQL/apply_llm.py)**: Integration layer connecting application requests to Groq and AWS Bedrock runtime client APIs.
- **[dbtables_schemas.py](file:///d:/Projects/TextToSQL/dbtables_schemas.py)** & **[dbtables_rules.py](file:///d:/Projects/TextToSQL/dbtables_rules.py)**: Contains standard database table DDLs and custom PostgreSQL rules utilized during prompt generation.
- **[example_cases.py](file:///d:/Projects/TextToSQL/example_cases.py)**: Preset network security questions and faulty SQL statements used for agent validation.

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
Start the Streamlit application to open the dashboard interface in your default browser:
```bash
streamlit run app.py
```
*(By default, it serves on [http://localhost:8501](http://localhost:8501))*

### Run Evaluation Test Cases (CLI)
To execute the reflection loop against preset test cases via terminal:
```bash
python main.py
```
