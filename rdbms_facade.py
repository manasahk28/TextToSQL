import sqlite3
from example_cases import get_example_case
from dbtables_schemas import get_schema_prompt_for_all_tables


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
    def execute_sql(self, sql_statements: [str]):

        # execute the SQL script
        rdbms_results, rdbms_status = self.execute_sql_script(sql_statements)

        # create a dictionary to store the RDBMS results
        results = {self.RDBMS_OUTPUT: rdbms_results, self.PROCESSING_STATUS: rdbms_status}

        # return the executed SQL
        return results

    # A method to execute the generated SQL script against a sqlite database
    def execute_sql_script(self, sql_statements: [str]):
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

        connection = sqlite3.connect(self.database)
        with connection:
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
                            # this happens when the last statement is DDL (not a query)
                            status = self.PROCESSING_STATUS_SUCCESS
                        elif len(cursor.description) > 0:
                            column_names = [x[0] for x in cursor.description]
                            results = [tuple(column_names)]
                            for r in result:
                                results.append(r)
                            status = self.PROCESSING_STATUS_SUCCESS
                    else:
                        iterations += 1
            except Exception  as e:
                status = self.PROCESSING_STATUS_FAILED
                print(f"Error executing sql statement: {stmt} :{e}")
            finally:
                cursor.close()

        return results, status


    def validate_sql(self, query: str) -> bool:

        new_statements = get_schema_prompt_for_all_tables()
        new_statements.append(query)
        results = self.execute_sql(new_statements)
        if results[self.PROCESSING_STATUS] ==  self.PROCESSING_STATUS_FAILED:
            print(query)
            print(results)
            return False
        return True