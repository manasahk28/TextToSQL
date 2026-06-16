import sqlite3
from tests.example_cases import get_example_case
from src.database.dbtables_schemas import get_schema_prompt_for_all_tables


# The class RdbmsFacade wraps one or more SQL Database Engines to provide a consistent interface
# independent of the underlying implementation
# For this implementation only sqlite is supported

class RdbmsFacade:

    RDBMS_OUTPUT = 'rdbms_output'
    PROCESSING_STATUS = 'processing_status'
    PROCESSING_STATUS_SUCCESS = 'success'
    PROCESSING_STATUS_FAILED = 'failed'

    def __init__(self, database: str):
        self.database = database

    # A method to execute SQL
    def execute_sql(self, sql_statements: list[str], rollback: bool = False):

        # execute the SQL script
        rdbms_results, rdbms_status, error_msg = self.execute_sql_script(sql_statements, rollback=rollback)

        # create a dictionary to store the RDBMS results
        results = {
            self.RDBMS_OUTPUT: rdbms_results,
            self.PROCESSING_STATUS: rdbms_status,
            'error_message': error_msg
        }

        # return the executed SQL
        return results

    # A method to execute the generated SQL script against a sqlite database
    def execute_sql_script(self, sql_statements: list[str], rollback: bool = False):
        """
        This method executes the SQL script against a sqlite database.
        It will execute each statement in the SQL script and return the results of the last statement.
        Success is defined as a valid query execution for the last statement.
        This is determined by checking if the cursor did not throw an error, and it has a row description.
        :param sql_statements: the SQL statements to execute
        :return:
        """

        status, verbose = "failed", False
        results, iterations = [], 1
        error_msg = ""

        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        try:
            for stmt in sql_statements:
                if stmt == '':
                    iterations += 1
                    continue
                cursor.execute(stmt)
                result = cursor.fetchall()

                if result:
                    if verbose:
                        print(f"Rows resulting from SQL statement '{stmt}':")
                        for res in result:
                            print(res)
                else:
                    if verbose:
                        print(f"No rows resulting from SQL statement '{stmt}'\n")

                if iterations == len(sql_statements):
                    if cursor.description is None:
                        # this happens when the last statement is DDL/DML (not a query returning rows)
                        status = self.PROCESSING_STATUS_SUCCESS
                    elif len(cursor.description) > 0:
                        column_names = [x[0] for x in cursor.description]
                        results = [tuple(column_names)]
                        for r in result:
                            results.append(r)
                        status = self.PROCESSING_STATUS_SUCCESS
                else:
                    iterations += 1

            if rollback:
                connection.rollback()
            else:
                connection.commit()
        except Exception  as e:
            try:
                connection.rollback()
            except Exception:
                pass
            status = self.PROCESSING_STATUS_FAILED
            error_msg = str(e)
            print(f"Error executing sql statement: {stmt} :{e}")
        finally:
            cursor.close()
            connection.close()

        return results, status, error_msg


    def validate_sql(self, query: str, schema_prompts: list[str] = None) -> tuple[bool, str]:

        if self.database == ":memory:":
            if schema_prompts is None:
                schema_prompts = get_schema_prompt_for_all_tables()
            new_statements = list(schema_prompts)
        else:
            new_statements = []

        new_statements.append(query)
        results = self.execute_sql(new_statements, rollback=True)
        if results[self.PROCESSING_STATUS] ==  self.PROCESSING_STATUS_FAILED:
            print(query)
            print(results)
            return False, results.get('error_message', 'Unknown database error')
        return True, ""


def is_select_query(query: str) -> bool:
    """
    Check if the SQL query is a read-only query (starts with SELECT or WITH)
    after cleaning comments and leading/trailing whitespace.
    """
    import re
    # Strip single line comments starting with -- or #
    q = re.sub(r'(?:--|#).*$', '', query, flags=re.MULTILINE)
    # Strip multi-line comments
    q = re.sub(r'/\*.*?\*/', '', q, flags=re.DOTALL)
    # Clean whitespace
    q = q.strip().upper()
    return q.startswith("SELECT") or q.startswith("WITH")


def insert_mock_data(connection):
    """
    Populates the SQLite database tables with realistic mock data.
    """
    cursor = connection.cursor()
    try:
        # Insert access policies
        cursor.execute("""
        INSERT INTO access_policy (name, id, last_modified_date, last_modified_by, lowfilter_policy_id, cypher_policy_id, description) 
        VALUES ('Default Access Policy', 1, '2026-06-01 10:00:00', 'admin', NULL, NULL, 'Standard access policy for office network');
        """)
        cursor.execute("""
        INSERT INTO access_policy (name, id, last_modified_date, last_modified_by, lowfilter_policy_id, cypher_policy_id, description) 
        VALUES ('Guest Access Policy', 2, '2026-06-05 14:00:00', 'user1', NULL, NULL, 'Restricted policy for guests');
        """)
        cursor.execute("""
        INSERT INTO access_policy (name, id, last_modified_date, last_modified_by, lowfilter_policy_id, cypher_policy_id, description) 
        VALUES ('HQ Access Policy', 3, '2026-06-12 09:30:00', 'admin', 10, NULL, 'Secure policy for headquarters');
        """)

        # Insert access rules
        cursor.execute("""
        INSERT INTO access_rule (enabled, action, id, ips_policy_id, name, access_policy_id, last_modified_date, description) 
        VALUES (1, 'ALLOW', 101, 201, 'Allow HTTP/HTTPS', 1, '2026-06-01 10:05:00', 'Allow web browsing');
        """)
        cursor.execute("""
        INSERT INTO access_rule (enabled, action, id, ips_policy_id, name, access_policy_id, last_modified_date, description) 
        VALUES (1, 'BLOCK', 102, NULL, 'Block Torrent', 1, '2026-06-01 10:10:00', 'Block peer-to-peer file sharing');
        """)
        cursor.execute("""
        INSERT INTO access_rule (enabled, action, id, ips_policy_id, name, access_policy_id, last_modified_date, description) 
        VALUES (0, 'MONITOR', 103, 202, 'Monitor SSH', 2, '2026-06-05 14:15:00', 'Log all SSH traffic');
        """)

        # Insert intrusion policies
        cursor.execute("""
        INSERT INTO intrusion_policy (inline_mode, name, base_policy_id, id, domain_id, base_policy_name, description) 
        VALUES (1, 'Baseline Detection', 501, 201, 1, 'Default Base', 'Detect standard threats');
        """)
        cursor.execute("""
        INSERT INTO intrusion_policy (inline_mode, name, base_policy_id, id, domain_id, base_policy_name, description) 
        VALUES (1, 'Strict Prevention', 502, 202, 1, 'Secure Base', 'Aggressively block suspicious activity');
        """)

        # Insert VPN policy unions
        cursor.execute("""
        INSERT INTO vpn_policy_union (name, description, id, policy_type, last_modified_date, last_modified_by, domain_id) 
        VALUES ('Corporate VPN', 'VPN for employees', 301, 'VPN', '2026-06-02 08:00:00', 'admin', 1);
        """)
        cursor.execute("""
        INSERT INTO vpn_policy_union (name, description, id, policy_type, last_modified_date, last_modified_by, domain_id) 
        VALUES ('Jaguar Rule 1', 'Jaguar specific VPN rules', 302, 'JaguarVPN', '2026-06-04 11:30:00', 'admin', 1);
        """)
        cursor.execute("""
        INSERT INTO vpn_policy_union (name, description, id, policy_type, last_modified_date, last_modified_by, domain_id) 
        VALUES ('Partner VPN', 'VPN for third-party partners', 303, 'VPN', '2026-06-14 16:00:00', 'user2', 1);
        """)

        # Insert firewall rule hit counts
        cursor.execute("""
        INSERT INTO firewall_rule_hit_count (hit_count, first_hit_time_stamp, last_hit_time_stamp, domain_id, hitcount_type, rule_name, rule_id, policy_name, policy_id, firewall_name, firewall_id) 
        VALUES (150, '2026-06-10 10:00:00', '2026-06-15 15:00:00', 1, 'accessPolicy', 'Allow HTTP/HTTPS', 101, 'Default Access Policy', 1, 'Firewall-A', 901);
        """)
        cursor.execute("""
        INSERT INTO firewall_rule_hit_count (hit_count, first_hit_time_stamp, last_hit_time_stamp, domain_id, hitcount_type, rule_name, rule_id, policy_name, policy_id, firewall_name, firewall_id) 
        VALUES (0, '2026-06-11 11:00:00', '2026-06-11 11:00:00', 1, 'accessPolicy', 'Block Torrent', 102, 'Default Access Policy', 1, 'Firewall-A', 901);
        """)

        # Insert firewall policy hit counts
        cursor.execute("""
        INSERT INTO firewall_policy_hit_count (hit_count, first_hit_time_stamp, last_hit_time_stamp, domain_id, hitcount_type, policy_name, policy_id, firewall_name, firewall_id) 
        VALUES (150, '2026-06-10 10:00:00', '2026-06-15 15:00:00', 1, 'accessPolicy', 'Default Access Policy', 1, 'Firewall-A', 901);
        """)
        cursor.execute("""
        INSERT INTO firewall_policy_hit_count (hit_count, first_hit_time_stamp, last_hit_time_stamp, domain_id, hitcount_type, policy_name, policy_id, firewall_name, firewall_id) 
        VALUES (45, '2026-06-12 08:30:00', '2026-06-15 12:45:00', 1, 'accessPolicy', 'Guest Access Policy', 2, 'Firewall-B', 902);
        """)

        connection.commit()
    except Exception as e:
        print(f"Error inserting mock data: {e}")


def get_dataframe_from_sql(query: str, db_path: str = None):
    """
    Creates a database connection, executes the query, and returns a DataFrame.
    If db_path is None or :memory:, it uses an in-memory DB populated with default mock data.
    """
    import pandas as pd

    if db_path is not None and db_path != ":memory:":
        connection = sqlite3.connect(db_path)
        try:
            if is_select_query(query):
                df = pd.read_sql_query(query, connection)
                return df
            else:
                cursor = connection.cursor()
                cursor.execute(query)
                connection.commit()
                rows_affected = cursor.rowcount
                df = pd.DataFrame([{
                    "Status": "Query executed successfully",
                    "Rows Affected": rows_affected
                }])
                return df
        except Exception as e:
            print(f"Error loading query into dataframe: {e}")
            raise e
        finally:
            connection.close()
    else:
        connection = sqlite3.connect(":memory:")
        try:
            # Create tables
            schema_statements = get_schema_prompt_for_all_tables()
            for stmt in schema_statements:
                if stmt.strip():
                    connection.execute(stmt)

            # Insert mock data
            insert_mock_data(connection)

            if is_select_query(query):
                # Read query results into DataFrame
                df = pd.read_sql_query(query, connection)
                return df
            else:
                cursor = connection.cursor()
                cursor.execute(query)
                connection.commit()
                rows_affected = cursor.rowcount
                df = pd.DataFrame([{
                    "Status": "Query executed successfully",
                    "Rows Affected": rows_affected
                }])
                return df
        except Exception as e:
            print(f"Error loading query into dataframe: {e}")
            raise e
        finally:
            connection.close()