import unittest

from mock import Mock, patch

from lib.activity_mgr import ActivityMgr, SELECTION, EVENT, SPORT


class ActivityMgrUnitTests(unittest.TestCase):

    def setUp(self):
        db = Mock()
        self.mgr = ActivityMgr(db, **{})

    def test_set_activity_type__sport(self):
        self.mgr.set_activity_type()
        self.assertEqual("sport", self.mgr.activity_type)

    def test_set_activity_type__event(self):
        self.mgr.all_args['sport'] = 'sport'
        self.mgr.set_activity_type()
        del self.mgr.all_args['sport']
        self.assertEqual("event", self.mgr.activity_type)

    def test_set_activity_type__selection(self):
        self.mgr.all_args['event'] = 'event'
        self.mgr.set_activity_type()
        del self.mgr.all_args['event']
        self.assertEqual("selection", self.mgr.activity_type)

    @patch('lib.activity_mgr.ActivityMgr.disable_sport')
    def test_end_activity__ends_sport(self, mock_disable):
        self.mgr.end_activity()
        self.assertEqual(1, mock_disable.call_count)

    @patch('lib.activity_mgr.ActivityMgr.disable_event')
    def test_end_activity__ends_event(self, mock_disable):
        self.mgr.activity_type = EVENT
        self.mgr.end_activity()
        self.mgr.activity_type = None
        self.assertEqual(1, mock_disable.call_count)

    @patch('lib.activity_mgr.ActivityMgr.disable_selection')
    def test_end_activity__ends_selection(self, mock_disable):
        self.mgr.activity_type = SELECTION
        self.mgr.end_activity()
        self.mgr.activity_type = None
        self.assertEqual(1, mock_disable.call_count)

    @patch('lib.activity_mgr.ActivityMgr.disable_all_events_by_sport')
    def test_disable_sport__success(self, mock_disable):
        self.mgr.disable_sport(event_triggered=True)
        self.assertEqual(1, self.mgr.db.update_rows_inactive.call_count)
        self.assertEqual(0, mock_disable.call_count)

    @patch('lib.activity_mgr.ActivityMgr.disable_all_events_by_sport')
    def test_disable_sport__disables_child_events(self, mock_disable):
        self.mgr.disable_sport()
        self.assertEqual(1, self.mgr.db.update_rows_inactive.call_count)
        self.assertEqual(1, mock_disable.call_count)

    @patch('lib.activity_mgr.ActivityMgr.get_all_events_by_sport', return_value=[{'name': EVENT, 'active': 1}])
    @patch('lib.activity_mgr.ActivityMgr.disable_all_selections_by_event')
    @patch('lib.activity_mgr.ActivityMgr.disable_sport')
    def test_disable_event__success(self, mock_disable_sport, mock_disable_sel, _):
        self.mgr.db.select_all_from_table_by_key_value.return_value = [{'sport': SPORT}]
        self.mgr.disable_event()
        self.assertEqual(1, self.mgr.db.update_row.call_count)
        self.assertEqual(1, self.mgr.db.select_all_from_table_by_key_value.call_count)
        self.assertEqual(1, mock_disable_sel.call_count)
        self.assertEqual(0, mock_disable_sport.call_count)

    @patch('lib.activity_mgr.ActivityMgr.get_all_events_by_sport', return_value=[{'name': EVENT, 'active': 0}])
    @patch('lib.activity_mgr.ActivityMgr.disable_all_selections_by_event')
    @patch('lib.activity_mgr.ActivityMgr.disable_sport')
    def test_disable_event__disables_sport(self, mock_disable_sport, mock_disable_sel, _):
        self.mgr.db.select_all_from_table_by_key_value.return_value = [{'sport': SPORT}]
        self.mgr.disable_event()
        self.assertEqual(1, self.mgr.db.update_row.call_count)
        self.assertEqual(1, self.mgr.db.select_all_from_table_by_key_value.call_count)
        self.assertEqual(1, mock_disable_sel.call_count)
        self.assertEqual(1, mock_disable_sport.call_count)

    @patch('lib.activity_mgr.ActivityMgr.get_all_events_by_sport', return_value=[{'name': EVENT, 'active': 0}])
    @patch('lib.activity_mgr.ActivityMgr.disable_all_selections_by_event', return_value=[{'name': EVENT, 'active': 0}])
    def test_disable_all_events_by_sport__success(self, mock_disable_sel, _):
        self.mgr.disable_all_events_by_sport(SPORT)
        self.assertEqual(1, self.mgr.db.update_row.call_count)
        self.assertEqual(1, mock_disable_sel.call_count)

    def test_get_all_events_by_sport__success(self):
        self.mgr.get_all_events_by_sport(SPORT)
        self.assertEqual(1, self.mgr.db.select_all_from_table_by_key_value.call_count)

    @patch('lib.activity_mgr.ActivityMgr.get_all_selections_by_event', return_value=[{'name': SELECTION}])
    @patch('lib.activity_mgr.ActivityMgr.disable_event')
    def test_disable_selection__success(self, mock_disable, _):
        self.mgr.db.select_all_from_table_by_key_value.return_value = [{'event': EVENT}]
        self.mgr.disable_selection()
        self.assertEqual(1, self.mgr.db.update_row.call_count)
        self.assertEqual(1, mock_disable.call_count)

    @patch('lib.activity_mgr.ActivityMgr.get_all_selections_by_event', return_value=[{'name': SELECTION, 'active': 1}])
    @patch('lib.activity_mgr.ActivityMgr.disable_event')
    def test_disable_selection__does_not_disable_event(self, mock_disable, _):
        self.mgr.db.select_all_from_table_by_key_value.return_value = [{'event': EVENT}]
        self.mgr.disable_selection()
        self.assertEqual(1, self.mgr.db.update_row.call_count)
        self.assertEqual(0, mock_disable.call_count)

    def test_disable_all_selections_by_event__success(self):
        self.mgr.disable_all_selections_by_event(EVENT)
        self.assertEqual(1, self.mgr.db.update_row.call_count)

    def test_get_all_selections_by_event__success(self):
        self.mgr.get_all_selections_by_event(EVENT)
        self.assertEqual(1, self.mgr.db.select_all_from_table_by_key_value.call_count)

    @patch('lib.activity_mgr.slugify', return_value="slug")
    def test_create_activity__sport(self, _):
        self.mgr.create_activity()
        self.assertEqual(1, self.mgr.db.insert_into_table.call_count)
        self.mgr.db.insert_into_table.assert_called_with(['name', 'slug', 'active'], [('', 'slug', 1)])

    @patch('lib.activity_mgr.slugify', return_value="slug")
    def test_create_activity__event(self, _):
        self.mgr.activity_type = EVENT
        self.mgr.create_activity()
        self.mgr.activity_type = None
        self.assertEqual(1, self.mgr.db.insert_into_table.call_count)
        self.mgr.db.insert_into_table.assert_called_with(
            ['name', 'slug', 'active', 'scheduled_start', 'sport'],
            [('', 'slug', 1, '2021-10-15T19:30:39+00:00', None)])

    @patch('lib.activity_mgr.slugify', return_value="slug")
    def test_create_activity__selection(self, _):
        self.mgr.activity_type = SELECTION
        self.mgr.create_activity()
        self.mgr.activity_type = None
        self.assertEqual(1, self.mgr.db.insert_into_table.call_count)
        self.mgr.db.insert_into_table.assert_called_with(['name', 'active', 'price', 'event'], [('', 1, '0.00', None)])

    @patch('lib.activity_mgr.ActivityMgr.get_all_events_by_sport', return_value=[{'name': EVENT}])
    @patch('lib.activity_mgr.ActivityMgr.delete_selections_by_event')
    def test_delete_activity__sport_and_child_events_selections(self, mock_del_sel, _):
        self.mgr.delete_activity()
        self.assertEqual(1, mock_del_sel.call_count)
        self.assertEqual(2, self.mgr.db.delete_row.call_count)

    @patch('lib.activity_mgr.ActivityMgr.delete_selections_by_event')
    def test_delete_activity__event_and_child_selections(self, mock_del_sel):
        self.mgr.activity_type = EVENT
        self.mgr.delete_activity()
        self.mgr.activity_type = None
        self.assertEqual(1, mock_del_sel.call_count)
        self.assertEqual(1, self.mgr.db.delete_row.call_count)

    def test_delete_activity__selection(self):
        self.mgr.activity_type = SELECTION
        self.mgr.delete_activity()
        self.mgr.activity_type = None
        self.assertEqual(1, self.mgr.db.delete_row.call_count)

    @patch('lib.activity_mgr.ActivityMgr.get_all_selections_by_event', return_value=[{'name': SELECTION}])
    def test_delete_selections_by_event__success(self, _):
        self.mgr.delete_selections_by_event(EVENT)
        self.assertEqual(1, self.mgr.db.delete_row.call_count)


if __name__ == '__main__':
    unittest.main(verbosity=2)
