from mysql.connector import connect, Error

_host = "mysqldb"
_user = "root"
_password = "p@ssw0rd"


class DBConnection(object):

    def __init__(self, database, table=None):
        self.database = database
        self.connection_config = {'user': _user, 'password': _password, 'host': _host, 'raise_on_warnings': True}
        self.table = table
        self.cursor = None
        self.connection = None

    def execute_query(self, query, database=None, result_req=False, commit=False):
        """
        Function to execute a Query

        :param query: MySQl query to be executed
        :type query: str
        :param database: Name of the DB to execute the query against
        :type database: str
        :param result_req: Boolean indicating if the result of the query should be returned
        :type result_req: bool
        :param commit: Boolean indicating if the query needs to be committed to the db
        :type commit: bool

        :raise Error: raised if the query execution fails

        :return: Optional return of the result list
        :rtype: list|None
        """
        if database:
            self.connection_config.update({'database': database})
        try:
            self.connection = connect(**self.connection_config)
            self.cursor = self.connection.cursor()
            self.cursor.execute(query)
            if commit:
                self.connection.commit()
            if result_req:
                return self.get_result(self.cursor)
        except Error as e:
            print(f"Failed to execute query: {query}. Error encountered: {e}")
            raise
        finally:
            if getattr(self.cursor, 'close'):
                self.cursor.close()
            if getattr(self.connection, 'close'):
                self.connection.close()

    @staticmethod
    def get_result(cursor):
        """
        Function to fetch all results of a Query

        :param cursor: DB cursor instance
        :type: `CMySQLConnection.cursor`

        :return: List of results of the query
        :rtype: list
        """
        headers = [_[0] for _ in cursor.description]
        results = cursor.fetchall()
        result_data = []
        for result in results:
            result_data.append(dict(zip(headers, result)))
        return result_data

    def create_database(self):
        """
        Function to set the database timezone to UTC and create the database
        """
        self.execute_query("SET time_zone = '+00:00'")
        self.execute_query(f"CREATE DATABASE {self.database}")

    def drop_database(self):
        """
        Function to drop a database
        """
        self.execute_query(f"DROP DATABASE IF EXISTS {self.database}")

    def create_table(self, column_values):
        """
        Function to create a table

        :param column_values: String containing the columns to create
        :type column_values: str
        """
        self.execute_query(f"CREATE TABLE {self.table} ({column_values})", database=self.database)

    def drop_table(self):
        """
        Function to drop a table
        """
        self.execute_query(f"DROP TABLE IF EXISTS {self.table}", database=self.database)

    def insert_into_table(self, columns, values):
        """
        Function to insert into a table

        :param columns: List of names of the column to insert into
        :type columns: list
        :param values: List of values to be inserted into the corresponding columns
        :type values: list
        """
        cs_columns = ", ".join(columns)
        cs_values = ", ".join([str(value) for value in values])
        self.execute_query(
            f"INSERT INTO {self.table} ({cs_columns}) VALUES {cs_values}", database=self.database, commit=True)

    def update_row(self, values, col_name, row_name):
        """
        Function to update a row

        :param values: Columns, Values to be updated
        :type values: dict
        :param col_name: Name of the column to match
        :type col_name: str
        :param row_name: Value of the supplied column to be matched
        :type row_name: str
        """
        set_values = []
        for key, value in values.items():
            set_values.append(f"{key} = '{value}'")
        set_str = ", ".join(set_values)
        self.execute_query(
            f"UPDATE {self.table} SET {set_str} WHERE {col_name} = '{row_name}'", database=self.database, commit=True)

    def update_rows_inactive(self, key, value):
        """
        Function to select all matching from a table

        :param key: Name of the column to match
        :type key: str
        :param value: Value of the supplied column to be matched
        :type value: str
        """
        self.execute_query(
            f"UPDATE {self.table} SET active = 0 WHERE {key} = '{value}'", database=self.database, commit=True)

    def select_all_from_table(self):
        """
        Function to select all from a table

        :return: List of all entries of the table
        :rtype: list
        """
        return self.execute_query(f"SELECT * FROM {self.table}", database=self.database, result_req=True)

    def select_all_from_table_by_key_value(self, key, value):
        """
        Function to select all matching from a table

        :param key: Name of the column to match
        :type key: str
        :param value: Value of the supplied column to be matched
        :type value: str

        :return: List of matched entries
        :rtype: list
        """
        return self.execute_query(
            f"SELECT * FROM {self.table} WHERE {key} = '{value}'", database=self.database, result_req=True)

    def delete_row(self, key, value):
        """
        Function to delete a single row

        :param key: Name of the column to match
        :type key: str
        :param value: Value of the supplied column to be matched
        :type value: str
        """
        self.execute_query(f"DELETE FROM {self.table} WHERE {key} = '{value}'", database=self.database, commit=True)
