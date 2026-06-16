# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import json
# pyrefly: ignore [missing-import]
import plotly.express as px
import re
import os
import sys

# Ensure project root is in sys.path for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import importlib
from src.agent import reflection_tasks
from tests import example_cases
from src import app_constants
from src.database import rdbms_facade
from src.database import dbtables_schemas
from src.agent import apply_llm

importlib.reload(reflection_tasks)
importlib.reload(example_cases)
importlib.reload(app_constants)
importlib.reload(rdbms_facade)
importlib.reload(dbtables_schemas)
importlib.reload(apply_llm)


# Set page configuration
st.set_page_config(
    page_title="Text-to-SQL Agent Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom modern styles
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header Container */
    .header-container {
        background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 20px -5px rgba(79, 70, 229, 0.2);
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.05em;
    }
    .header-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* Sleek container divider */
    .custom-hr {
        height: 2px;
        background: linear-gradient(90deg, transparent, #4f46e5, transparent);
        border: none;
        margin: 1.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🤖 Text-to-SQL Agent Dashboard</h1>
        <p class="header-subtitle">Real-time Chain-of-Thought Self-Correction, Live SQL Validation & Data Analytics</p>
    </div>
""", unsafe_allow_html=True)


# Sidebar Configuration
st.sidebar.header("⚙️ Configuration")

# Model and Provider Selection
st.sidebar.subheader("LLM Configuration")
provider = st.sidebar.selectbox(
    "Provider",
    ["Groq (Recommended)", "AWS Bedrock"]
)

if provider == "Groq (Recommended)":
    # Check if key is available
    has_key = os.environ.get("GROQ_API_KEY") is not None
    if has_key:
        st.sidebar.success("✅ GROQ_API_KEY found in environment")
    else:
        st.sidebar.warning("⚠️ GROQ_API_KEY not found in environment. Please add it to your .env file.")
        
    model = st.sidebar.selectbox(
        "Model",
        [
            "llama-3.1-8b-instant (Fast, High Limits)",
            "llama-3.3-70b-versatile (Powerful, Low Limits)",
            "mixtral-8x7b-32768"
        ],
        index=0
    )
    # Extract model identifier
    model_id = model.split(" ")[0]
else:
    model = st.sidebar.selectbox(
        "Model",
        [
            "anthropic.claude-3-haiku-20240307-v1:0 (Haiku)",
            "anthropic.claude-3-5-sonnet-20240620-v1:0 (Sonnet 3.5)"
        ],
        index=0
    )
    # Extract model identifier
    model_id = model.split(" ")[0]

# Apply model selection
apply_llm.set_LLM_model(model_id)

# Helper to extract schema DDL statements from SQLite database files
def extract_schema_from_sqlite(db_file_path):
    import sqlite3
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        schema_prompts = []
        for table in tables:
            if table[0]:
                schema_prompts.append(table[0])
        return schema_prompts
    except Exception as e:
        st.error(f"Error reading database schema: {e}")
        return []
    finally:
        conn.close()


# Helper to load CSV into SQLite table
def load_csv_to_sqlite(uploaded_file, db_file_path):
    import pandas as pd
    import sqlite3

    base_name = os.path.basename(uploaded_file.name)
    table_name = os.path.splitext(base_name)[0]
    table_name = re.sub(r'[^a-zA-Z0-9_]', '_', table_name).lower()

    try:
        df = pd.read_csv(uploaded_file)
        conn = sqlite3.connect(db_file_path)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.commit()
        conn.close()
        return table_name
    except Exception as e:
        st.error(f"Error loading CSV to SQLite: {e}")
        return None


# File Uploader in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("📂 Upload Custom Data Source")
uploaded_file = st.sidebar.file_uploader(
    "Upload a SQLite Database (.db/.sqlite) or a CSV File (.csv)",
    type=["db", "sqlite", "csv"]
)

db_path = ":memory:"
schema_prompts = None
custom_db_active = False

if uploaded_file is not None:
    custom_db_active = True
    temp_db_name = "temp_user.db"

    if uploaded_file.name.endswith(".csv"):
        table_name = load_csv_to_sqlite(uploaded_file, temp_db_name)
        if table_name:
            db_path = temp_db_name
            schema_prompts = extract_schema_from_sqlite(temp_db_name)
            st.sidebar.success(f"✅ Loaded CSV into table '{table_name}'")
    else:
        # Save uploaded SQLite database bytes to local file
        with open(temp_db_name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        db_path = temp_db_name
        schema_prompts = extract_schema_from_sqlite(temp_db_name)
        st.sidebar.success("✅ Loaded SQLite Database")

    # Display the table schemas in sidebar
    if schema_prompts:
        with st.sidebar.expander("📁 Detected Table Schemas", expanded=True):
            for schema in schema_prompts:
                # Find table name
                tbl_match = re.search(r'CREATE TABLE\s+"?([a-zA-Z0-9_]+)"?', schema, re.IGNORECASE)
                tbl_name = tbl_match.group(1) if tbl_match else "Table"
                st.markdown(f"**{tbl_name}**")
                st.code(schema, language="sql")

# Presets Section
st.sidebar.markdown("---")
st.sidebar.subheader("📝 Preset Queries")

if custom_db_active:
    use_preset = False
    st.sidebar.info("ℹ️ Presets disabled for custom data sources. Please enter a custom query.")
    user_query = st.text_input("Ask a question about your custom data:", "Show all records from the table")
else:
    use_preset = st.sidebar.checkbox("Use a preset query", value=True)
    selected_preset_idx = None
    if use_preset:
        presets = [
            "Case 0: List my VPN Policies (Simple Filter)",
            "Case 1: Which VPN policies are modified by 'admin'? (Multiple Filters)",
            "Case 2: Which ACP policies have assigned intrusion? (Requires Join - Schema Failure)",
            "Case 3: What are my never hit rules? (Aggregation & JOIN)",
            "Case 4: Which policies have hit counts > 0? (UNION/Subquery)",
            "Case 5: List VPN policies that are a VPN type (Duplicate Name Filter)",
            "Case 6: Is there an intrusion policy named 'Baseline Detection'? (Invalid Column)"
        ]
        preset_selection = st.sidebar.selectbox("Select Preset Case", presets, index=2) # Default to Case 2 to show validation error fix
        selected_preset_idx = presets.index(preset_selection)

        # Load preset query
        preset_case = example_cases.get_example_case(selected_preset_idx)
        user_query = preset_case["user_query"]
    else:
        user_query = st.text_input("Ask a question about your database schemas:", "List all intrusion policies and their details")

# Main Interface
st.subheader("💬 User Request")
st.info(f"**Question:** {user_query}")

# Define first pass generator for custom queries
def generate_first_pass_sql(query, schema_prompts=None):
    if schema_prompts is None:
        tables_schema = dbtables_schemas.get_schema_prompt_for_all_tables()
        rules_str = """Rules:
- When selecting VPN information from 'vpn_policy_union', filter policy_type = 'VPN'.
- To filter who modified a record, use 'last_modified_by'.
- Only use one of 'firewall_policy_hit_count' or 'firewall_rule_hit_count'.
- Do not add an ORDER BY unless explicitly asked.
- access_policy must join with access_rule to check for intrusion_policy."""
    else:
        tables_schema = schema_prompts
        rules_str = "Rules: None (Use standard SQL practices to answer the question based strictly on the schemas provided)."

    prompt = f"""You are a PostgreSQL expert and network firewall database expert.
Your job is to write a PostgreSQL query to answer the user's question based on the database schemas provided.

Schemas:
{tables_schema}

{rules_str}

Please output the SQL query inside <sql>...</sql> tags. Do not output any explanation or markdown outside the tags.

Question: {query}
"""
    response = apply_llm.get_llm_response(prompt)
    if not response:
        return ""
    sql = reflection_tasks.get_sql_from_completion(response)
    return sql.strip() if sql else ""

# Visualizer renderer
def render_plotly_visualization(df):
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns.tolist()

    # Treat strings that look like dates as datetime_cols
    for col in categorical_cols[:]:
        if df[col].astype(str).str.match(r'^\d{4}-\d{2}-\d{2}').any():
            categorical_cols.remove(col)
            datetime_cols.append(col)

    st.write("Choose a chart type to visualize the results:")

    chart_type = st.selectbox(
        "Chart Type",
        ["Auto-Select", "Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot"],
        key="viz_selector"
    )

    # Auto Selection logic
    if chart_type == "Auto-Select":
        if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
            chart_type = "Bar Chart"
        elif len(numeric_cols) >= 1 and len(datetime_cols) >= 1:
            chart_type = "Line Chart"
        elif len(categorical_cols) >= 1:
            chart_type = "Pie Chart"
        elif len(numeric_cols) >= 2:
            chart_type = "Scatter Plot"
        else:
            chart_type = "Bar Chart"

    # Setup chart selections
    if chart_type == "Bar Chart":
        x_axis = st.selectbox("X Axis (Categorical)", categorical_cols + datetime_cols + numeric_cols, index=0 if categorical_cols else 0, key="bar_x")
        y_axis = st.selectbox("Y Axis (Numeric)", numeric_cols + categorical_cols, index=0 if numeric_cols else 0, key="bar_y")

        if x_axis and y_axis:
            fig = px.bar(
                df, x=x_axis, y=y_axis,
                title=f"{y_axis} by {x_axis}",
                color_discrete_sequence=["#4f46e5"],
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Line Chart":
        x_axis = st.selectbox("X Axis (Time/Numeric)", datetime_cols + numeric_cols + categorical_cols, index=0 if datetime_cols else 0, key="line_x")
        y_axis = st.selectbox("Y Axis (Numeric)", numeric_cols, index=0 if numeric_cols else 0, key="line_y")

        if x_axis and y_axis:
            fig = px.line(
                df, x=x_axis, y=y_axis,
                title=f"{y_axis} over {x_axis}",
                color_discrete_sequence=["#06b6d4"],
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Pie Chart":
        names_col = st.selectbox("Names Column (Categorical)", categorical_cols + datetime_cols + numeric_cols, index=0 if categorical_cols else 0, key="pie_names")
        values_col = st.selectbox("Values Column (Numeric/Count)", [None] + numeric_cols, key="pie_values")

        if names_col:
            if values_col is None:
                df_counts = df[names_col].value_counts().reset_index()
                df_counts.columns = [names_col, "Count"]
                fig = px.pie(
                    df_counts, names=names_col, values="Count",
                    title=f"Distribution of {names_col}",
                    template="plotly_dark"
                )
            else:
                fig = px.pie(
                    df, names=names_col, values=values_col,
                    title=f"Distribution of {values_col} by {names_col}",
                    template="plotly_dark"
                )
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Scatter Plot":
        x_axis = st.selectbox("X Axis (Numeric)", numeric_cols + datetime_cols + categorical_cols, index=0 if len(numeric_cols) > 0 else 0, key="scatter_x")
        y_axis = st.selectbox("Y Axis (Numeric)", numeric_cols + categorical_cols, index=1 if len(numeric_cols) > 1 else 0, key="scatter_y")
        color_by = st.selectbox("Color By (Optional)", [None] + categorical_cols, key="scatter_color")

        if x_axis and y_axis:
            fig = px.scatter(
                df, x=x_axis, y=y_axis, color=color_by,
                title=f"{y_axis} vs {x_axis}",
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)


# Initialize session state for execution trace
if "result_trace" not in st.session_state:
    st.session_state.result_trace = None

# Detect any changes to current configuration inputs
current_config = {
    "query": user_query,
    "db_active": custom_db_active,
    "preset_idx": selected_preset_idx if 'selected_preset_idx' in locals() else None,
    "model": model,
    "provider": provider
}

if st.session_state.result_trace is not None:
    # If the inputs change, clear the cached query results
    if st.session_state.result_trace.get("config") != current_config:
        st.session_state.result_trace = None

# Run Button
if st.button("🚀 Execute Text-to-SQL Agent", use_container_width=True):
    if not user_query:
        st.warning("Please enter a question or select a preset case.")
    else:
        # Generate the execution trace
        if not custom_db_active and use_preset and selected_preset_idx is not None:
            # Load the preset with its pre-configured first-pass SQL (often containing syntax/schema errors)
            reflection_state = example_cases.get_example_case(selected_preset_idx).copy()
        else:
            # Generate the first pass SQL using the LLM
            with st.spinner("Generating first-pass SQL query..."):
                first_pass_sql = generate_first_pass_sql(user_query, schema_prompts=schema_prompts)

            reflection_state = {
                "user_query": user_query,
                "sql": first_pass_sql,
            }

        # Add dynamic DB path and custom schema prompts to state
        reflection_state["db_path"] = db_path
        reflection_state["schema_prompts"] = schema_prompts

        reflection_tasks.set_iteration_in_genoutput(reflection_state, 0)
        reflection_tasks.set_source_in_genoutput(reflection_state, 'First-pass')

        iteration = 0
        success = False
        final_sql = ""
        steps = []
        df = None

        # Self-correction loop
        with st.spinner("Agent is running self-correction loop..."):
            while True:
                current_sql = reflection_state.get('sql', '').strip()

                # 1. Run Validation (against SQLite Facade)
                validation_result = reflection_tasks.validation(reflection_state)
                is_valid = validation_result['validation']
                validation_msg = validation_result['validation_analysis']

                step_data = {
                    "attempt": iteration + 1,
                    "sql": current_sql,
                    "is_valid": is_valid,
                    "validation_msg": validation_msg if not is_valid else None,
                    "thinking": None,
                    "next_sql": None
                }

                if is_valid:
                    success = True
                    final_sql = current_sql
                    steps.append(step_data)
                    break

                if iteration >= app_constants.MAX_REFLECTION_ITERATIONS:
                    steps.append(step_data)
                    break

                # 2. Reflect and Remedy
                iteration += 1
                
                # Prepare reflection prompt (which contains the validation_msg error)
                reflection_prompt = reflection_tasks.generate_reflection_prompt(reflection_state)

                # Call LLM
                llm_response = apply_llm.get_llm_response(reflection_prompt)

                if not llm_response:
                    step_data["validation_msg"] = "Error: Failed to receive response from the LLM."
                    steps.append(step_data)
                    break

                # Extract thoughts and SQL
                thinking = reflection_tasks.get_thinking_from_completion(llm_response)
                next_sql = reflection_tasks.get_sql_from_completion(llm_response)

                step_data["thinking"] = thinking
                step_data["next_sql"] = next_sql
                steps.append(step_data)

                # Update reflection state for next loop
                reflection_tasks.set_sql_in_genoutput(reflection_state, next_sql)
                reflection_tasks.set_iteration_in_genoutput(reflection_state, iteration)
                reflection_tasks.set_source_in_genoutput(reflection_state, 'Reflection')

        # After loop concludes, fetch data if successful
        if success:
            try:
                df = rdbms_facade.get_dataframe_from_sql(final_sql, db_path=db_path)
            except Exception as e:
                success = False
                steps[-1]["is_valid"] = False
                steps[-1]["validation_msg"] = f"Error executing final query: {e}"

        # Store results in session state
        st.session_state.result_trace = {
            "steps": steps,
            "success": success,
            "final_sql": final_sql,
            "df": df,
            "is_select": rdbms_facade.is_select_query(final_sql) if (success and final_sql) else False,
            "config": current_config
        }
        st.rerun()

# Rendering Block
if st.session_state.result_trace is not None:
    trace = st.session_state.result_trace

    st.markdown("<hr class='custom-hr'>", unsafe_allow_html=True)
    st.subheader("⛓️ Agent Execution and Chain-of-Thought Trace")

    for step in trace["steps"]:
        st.markdown(f"#### 🤖 Attempt {step['attempt']}")
        st.markdown("**Generated SQL:**")
        st.code(step["sql"], language="sql")

        if not step["is_valid"]:
            st.error(f"❌ **Database Validation Failed**\n\n`{step['validation_msg']}`")
            if step["thinking"]:
                with st.expander(f"💭 Attempt {step['attempt']} ── Agent Reflection & Correction Plan", expanded=True):
                    st.markdown("**Agent's Reasoning:**")
                    st.write(step["thinking"])
                    if step["next_sql"]:
                        st.markdown("**Remedied SQL for Next Attempt:**")
                        st.code(step["next_sql"], language="sql")
        else:
            st.success("✅ **Database Validation Succeeded**")

    # After loop concludes:
    st.markdown("<hr class='custom-hr'>", unsafe_allow_html=True)

    if trace["success"]:
        st.success("🎉 **Success! Correct SQL Query Secured.**")

        # Display Final SQL
        st.subheader("📄 Final Executable SQL")
        st.code(trace["final_sql"], language="sql")

        # 3. Fetch Data & Display
        st.subheader("📊 Query Results")
        df = trace["df"]
        if df is None or df.empty:
            st.info("The query executed successfully but returned 0 rows.")
        else:
            st.dataframe(df, use_container_width=True)

            # Only render Plotly Visualizations for SELECT queries
            if trace["is_select"]:
                st.subheader("📈 Custom Data Analytics")
                render_plotly_visualization(df)
    else:
        st.error("❌ **Agent failed to resolve the database issue within the reflection limit.**")
