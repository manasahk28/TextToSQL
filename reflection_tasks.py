import re

import apply_llm
import dbtables_schemas
import dbtables_rules
import rdbms_facade

# Functions for reflection related tasks:
# o  validation - to validate the generated SQL
# o  generate_reflection_prompt - to prepare the prompt for reflection
# o  llm_inference - to use the prepared prompt to review and remedy

reflection_system_prompt = """
You are a PostgreSQL expert and also a network firewall expert. 
Your job is to review a SQL query that has been created to answer a user's question.
That SQL may have been created without fully considering the sql schema definitions and the associated rules.

You will be given the user's question in natural language.
You will be given the SQL query that was created to answer the question.
You will also be given the schema of the tables and the rules for the tables that are used in the sql query.
Please study the structure of the given tables and the rules.

Review the user's question, the SQL query along with the supporting schema information and put your analysis within <thinking> tags.
Output what you determine to be the correct SQL query within <sql> tags.
The SQL output should be a syntactically correct postgres query

Do not output any further explanations or prose.
"""


def validation(reflection_state):
    # check reflection state for sql
    generated_sql = get_sql_from_genoutput(reflection_state)

    if not generated_sql:
        result = {
            'validation': False,
            'validation_analysis': "No SQL query was generated.",
        }
        return result

    # Check if there is a custom database path and schema prompts in state
    db_path = reflection_state.get('db_path', ':memory:')
    schema_prompts = reflection_state.get('schema_prompts', None)

    # check if the generated sql is syntactically/schema valid
    test_db = rdbms_facade.RdbmsFacade(db_path)
    is_valid, error_msg = test_db.validate_sql(generated_sql, schema_prompts=schema_prompts)

    if not is_valid:
        result = {
            'validation': False,
            'validation_analysis': f"The generated SQL is invalid. Database error: {error_msg}",
        }
    else:
        result = {
            'validation': True,
            'validation_analysis': "The generated SQL passed validation checks.",
        }
    return result


def generate_reflection_prompt(reflection_state):

    # extract fields from first pass output
    user_query = get_user_query_from_genoutput(reflection_state)
    generated_sql = get_sql_from_genoutput(reflection_state)

    schema_prompts = reflection_state.get('schema_prompts', None)
    if schema_prompts is None:
        # if there are any specific rules for the tables being used, get those rules
        tables_rules = dbtables_rules.get_all_rules_for_tables()
        tables_schema = dbtables_schemas.get_schema_prompt_for_all_tables()
    else:
        # Custom DB uploaded: bypass rules and use the custom DB schema
        tables_rules = []
        tables_schema = schema_prompts

    # Merge together the prompt elements to have a single prompt to pass to the LLM for reflection
    reflection_prompt = reflection_system_prompt + \
        user_query_prompt(user_query) + \
        prev_sql_prompt(generated_sql) + \
        schema_prompt(tables_schema) + \
        rules_prompt(tables_rules)

    return reflection_prompt


def llm_inference(prompt):
    return apply_llm.get_llm_response(prompt)


# 
# Helper functions for preparing parts- of the reflection prompt -
# user_query_prompt, schema_prompt, rules_prompt, prev_sql_prompt
# 
def user_query_prompt(user_query):
    return f"<user_question>\n{user_query}\n</user_question>\n"


def schema_prompt(schema):
    return f"<database_schema>\n{schema}\n</database_schema>\n"


def rules_prompt(rules):
    return f"<schema_rules>\n{rules}\n</schema_rules>\n"


def prev_sql_prompt(prev_sql):
    return f"<sql_query>\n{prev_sql}\n</sql_query>\n"


#
# helper functions to extract information pieces from llm response
# get_tag_from_completion, get_sql_from_completion, get_thinking_from_completion
# 
def get_sql_from_completion(completion):
    # The LLM prompt requests the SQL out to be between <sql> tags
    # this method uses regex to extract the SQL output from the  completion
    tag = "sql"
    return get_tag_from_completion(tag, completion)


def get_thinking_from_completion(completion):
    # The LLM prompt requests the thinking out to be between <thinking> tags
    tag = "thinking"
    return get_tag_from_completion(tag, completion)


def get_tag_from_completion(tag, completion):
    # The LLM prompt requests the thinking and SQL to be output between <tags>
    # this method uses regex to extract the <tag>> output from the completion

    if not completion or not isinstance(completion, str):
        return ""

    # regex to extract required strings
    reg_str = "<" + tag + ">(.*?)</" + tag + ">"
    tag_string = re.findall(reg_str, completion)

    if len(tag_string) > 0:
        tag_string = tag_string[0]
    else:
        tag_string = ""

    return tag_string


# 
# Helper functions to get and set fields from output reflection state object -
# get_tables_from_genoutput, get_sql_from_genoutput, get_user_query_from_genoutput, 
# set_iteration_in_genoutput, set_source_in_genoutput, set_sql_in_genoutput
#
def get_sql_from_genoutput(genoutput: dict):
    return genoutput['sql']


def get_user_query_from_genoutput(genoutput: dict):
    return genoutput['user_query']


def set_iteration_in_genoutput(genoutput, iteration):
    genoutput['iteration'] = iteration


def set_source_in_genoutput(genoutput, source):
    genoutput['source'] = source


def set_sql_in_genoutput(genoutput, sql):
    genoutput['sql'] = sql.strip()


# Helper function to print the prompt in a easy to read form.
# This function is used only for debugging purposes.
# this is the only function in this module that directly prints
def print_prompt(prompt_text):
    print("'''")
    # System prompt
    sysp_seg_end = prompt_text.find("<user_question>")
    sysp_seg_print_end = min(250, sysp_seg_end)
    trailig_start = max(sysp_seg_print_end, sysp_seg_end-320)  # using 320 is a cheat, it is the len of the last part of sys prompt
    if sysp_seg_print_end < sysp_seg_end:
        tag = '...'
    else:
        tag = ""
    print(f"{prompt_text[0:sysp_seg_print_end].strip()}{tag}\n{tag}{prompt_text[trailig_start:sysp_seg_end].strip()}\n")

    # User query, along with previously generated sql_query
    query_seg_end = prompt_text.find("<database_schema>")
    print(f"{prompt_text[sysp_seg_end:query_seg_end]}")

    # Database schema
    schema_seg_end = prompt_text.find("<schema_rules>")
    schema_seg_print_end = min(query_seg_end+400, schema_seg_end)
    if schema_seg_print_end < schema_seg_end:
        tag = '...'
    else:
        tag = ""
    print(f"{prompt_text[query_seg_end:schema_seg_print_end]}{tag}\n")

    # Database rules
    print(f"{prompt_text[schema_seg_end:]}")

    print("'''")