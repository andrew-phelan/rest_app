import unittest

from mock import patch

from lib.db_setup import setup_db, SPORTS_VALUES, EVENTS_VALUES, SELECTIONS_VALUES


class DbSetupUnitTests(unittest.TestCase):

    @patch('lib.db.DBConnection.drop_database')
    @patch('lib.db.DBConnection.create_database')
    @patch('lib.db.DBConnection.create_table')
    @patch('lib.db.DBConnection.insert_into_table')
    def test_setup_db__creates_all_tables(self, mock_insert, mock_create_table, mock_create_db, _):
        setup_db('test')
        self.assertEqual(1, mock_create_db.call_count)
        self.assertEqual(3, mock_create_table.call_count)
        mock_create_table.assert_any_call(SPORTS_VALUES)
        mock_create_table.assert_any_call(EVENTS_VALUES)
        mock_create_table.assert_called_with(SELECTIONS_VALUES)
        self.assertEqual(3, mock_insert.call_count)


if __name__ == '__main__':
    unittest.main(verbosity=2)
