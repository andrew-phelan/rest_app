import unittest

from mock import patch, Mock

from lib.db import DBConnection, Error


class DBUnitTests(unittest.TestCase):

    def setUp(self):
        self.db = DBConnection('test', 'test_table')
        self.columns = ['name', 'active']
        self.query = "query"

    @patch('lib.db.connect')
    def test_execute_query__creates_database(self, mock_connect):
        self.db.execute_query(self.query)
        self.assertEqual(1, mock_connect.call_count)
        mock_connect.assert_called_with(user='root', password='p@ssw0rd', host='mysqldb', raise_on_warnings=True)
        self.assertEqual(1, mock_connect.return_value.cursor.call_count)
        self.assertEqual(1, mock_connect.return_value.cursor.return_value.execute.call_count)
        self.assertEqual(1, mock_connect.return_value.cursor.return_value.close.call_count)
        self.assertEqual(1, mock_connect.return_value.close.call_count)

    @patch('lib.db.connect')
    def test_execute_query__commits_to_database(self, mock_connect):
        self.db.execute_query(self.query, database='db', commit=True)
        self.assertEqual(1, mock_connect.call_count)
        self.assertEqual(1, mock_connect.return_value.cursor.call_count)
        mock_connect.assert_called_with(
            user='root', password='p@ssw0rd', host='mysqldb', raise_on_warnings=True, database='db')
        self.assertEqual(1, mock_connect.return_value.cursor.return_value.execute.call_count)
        self.assertEqual(1, mock_connect.return_value.cursor.return_value.close.call_count)
        self.assertEqual(1, mock_connect.return_value.close.call_count)
        self.assertEqual(1, mock_connect.return_value.commit.call_count)

    @patch('lib.db.connect')
    @patch('lib.db.DBConnection.get_result')
    def test_execute_query__returns_result(self, mock_get_result, mock_connect):
        self.db.execute_query(self.query, database='db', result_req=True)
        self.assertEqual(1, mock_connect.call_count)
        self.assertEqual(1, mock_connect.return_value.cursor.call_count)
        mock_connect.assert_called_with(
            user='root', password='p@ssw0rd', host='mysqldb', raise_on_warnings=True, database='db')
        self.assertEqual(1, mock_connect.return_value.cursor.return_value.execute.call_count)
        self.assertEqual(1, mock_connect.return_value.cursor.return_value.close.call_count)
        self.assertEqual(1, mock_connect.return_value.close.call_count)
        self.assertEqual(1, mock_get_result.call_count)

    @patch('lib.db.connect', side_effect=Error('Some SQL Error'))
    def test_execute_query__raises_error(self, _):
        self.assertRaises(AttributeError, self.db.execute_query, self.query)

    def test_get_result__success(self):
        cursor = Mock()
        cursor.description = [('id',), ('name',), ('active',)]
        cursor.fetchall.return_value = [['1', 'Test1', 'True'], ['2', 'Test2', 'True']]
        results = self.db.get_result(cursor)
        expected = [{'id': '1', 'name': 'Test1', 'active': 'True'}, {'id': '2', 'name': 'Test2', 'active': 'True'}]
        self.assertListEqual(results, expected)

    @patch('lib.db.DBConnection.execute_query')
    def test_create_database__success(self, mock_execute):
        self.db.create_database()
        self.assertEqual(2, mock_execute.call_count)
        mock_execute.assert_any_call("SET time_zone = '+00:00'")
        mock_execute.assert_called_with("CREATE DATABASE test")

    @patch('lib.db.DBConnection.execute_query')
    def test_drop_database__success(self, mock_execute):
        self.db.drop_database()
        self.assertEqual(1, mock_execute.call_count)
        mock_execute.assert_called_with("DROP DATABASE IF EXISTS test")

    @patch('lib.db.DBConnection.execute_query')
    def test_create_table__success(self, mock_execute):
        values = ("id INT AUTO_INCREMENT NOT NULL PRIMARY KEY, name VARCHAR(32) NOT NULL, slug VARCHAR(32), "
                  "active BOOLEAN NOT NULL")
        expected = f"CREATE TABLE {self.db.table} ({values})"
        self.db.create_table(values)
        self.assertEqual(1, mock_execute.call_count)
        mock_execute.assert_called_with(expected, database='test')

    @patch('lib.db.DBConnection.execute_query')
    def test_drop_table__success(self, mock_execute):
        self.db.drop_table()
        self.assertEqual(1, mock_execute.call_count)
        mock_execute.assert_called_with("DROP TABLE IF EXISTS test_table", database='test')

    @patch('lib.db.DBConnection.execute_query')
    def test_insert_into_table__success(self, mock_execute):
        values = [('Test1', False), ('Test2', True), ('Test3', True)]
        self.db.insert_into_table(self.columns, values)
        expected = "INSERT INTO test_table (name, active) VALUES ('Test1', False), ('Test2', True), ('Test3', True)"
        self.assertEqual(1, mock_execute.call_count)
        mock_execute.assert_called_with(expected, database='test', commit=True)

    @patch('lib.db.DBConnection.execute_query')
    def test_update_row__success(self, mock_execute):
        values = {'key': 1, 'key1': 2}
        self.db.update_row(values, 'col', 'value')
        self.assertEqual(1, mock_execute.call_count)
        mock_execute.assert_called_with(
            "UPDATE test_table SET key = '1', key1 = '2' WHERE col = 'value'", database='test', commit=True)

    @patch('lib.db.DBConnection.execute_query')
    def test_update_rows_inactive__success(self, mock_execute):
        self.db.update_rows_inactive('key', 'value')
        self.assertEqual(1, mock_execute.call_count)
        mock_execute.assert_called_with(
            "UPDATE test_table SET active = 0 WHERE key = 'value'", database='test', commit=True)

    @patch('lib.db.DBConnection.execute_query', return_value=["Some Output"])
    def test_select_all_from_table__success(self, mock_execute):
        res = self.db.select_all_from_table()
        self.assertIsNotNone(res)
        self.assertEqual(1, mock_execute.call_count)
        mock_execute.assert_called_with("SELECT * FROM test_table", database='test', result_req=True)

    @patch('lib.db.DBConnection.execute_query', return_value=["Some Output"])
    def test_select_all_from_table_by_key_value__success(self, mock_execute):
        res = self.db.select_all_from_table_by_key_value('key', 'val')
        self.assertIsNotNone(res)
        self.assertEqual(1, mock_execute.call_count)
        mock_execute.assert_called_with("SELECT * FROM test_table WHERE key = 'val'", database='test', result_req=True)

    @patch('lib.db.DBConnection.execute_query')
    def test_delete_row__success(self, mock_execute):
        self.db.delete_row('key', 'value')
        self.assertEqual(1, mock_execute.call_count)
        mock_execute.assert_called_with("DELETE FROM test_table WHERE key = 'value'", database='test', commit=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
