from datetime import datetime

from slugify import slugify

SPORT = "sport"
EVENT = "event"
SELECTION = "selection"


class ActivityMgr(object):

    def __init__(self, db, **kwargs):
        self.db = db
        self.activity_type = None
        self.status = None
        self.outcome = None
        self.all_args = kwargs

    def set_activity_type(self):
        """
        Function to determine the activity type
        """
        if 'outcome' in self.all_args.keys() or 'event' in self.all_args.keys():
            self.activity_type = SELECTION
        elif 'status' in self.all_args.keys() or 'sport' in self.all_args.keys():
            self.activity_type = EVENT
        else:
            self.activity_type = SPORT

    def end_activity(self):
        """
        Function to end any activity
        """
        if self.activity_type == SELECTION:
            self.disable_selection()
        elif self.activity_type == EVENT:
            self.disable_event()
        else:
            self.disable_sport()

    def disable_sport(self, event_triggered=False):
        """
        Function to disable a sport

        :param event_triggered: Boolean indicating if all child events are inactive
        :type event_triggered: bool
        """
        sport_name = self.all_args.get('name')
        if not event_triggered:
            self.disable_all_events_by_sport(sport_name)
        self.db.table = 'sports'
        self.db.update_rows_inactive('name', sport_name)

    def disable_event(self):
        """
        Function to disable an event and and update parent sport if all events inactive
        """
        self.db.table = 'events'
        event_name = self.all_args.get('name')
        status = self.all_args.get('status', 3)
        self.db.update_row({'active': 0, 'status': status}, 'name', event_name)
        sport_name = self.db.select_all_from_table_by_key_value('name', event_name)[0].get(SPORT)
        events = self.get_all_events_by_sport(sport_name)
        self.disable_all_selections_by_event(event_name)
        if not any([event.get('active') for event in events]):
            self.all_args['name'] = sport_name
            self.disable_sport(event_triggered=True)

    def disable_all_events_by_sport(self, sport_name):
        """
        Function to disable all child events of a sport

        :param sport_name: Name of the parent sport
        :type sport_name: str
        """
        self.db.table = 'events'
        status = self.all_args.get('status', 3)
        self.db.update_row({'active': 0, 'status': status}, 'sport', sport_name)
        events = self.get_all_events_by_sport(sport_name)
        for event in events:
            self.disable_all_selections_by_event(event.get('name'))

    def get_all_events_by_sport(self, sport_name):
        """
        Function to fetch all events of a sport

        :param sport_name: Name of the parent sport
        :type sport_name: str

        :return: List of child events
        :rtype: list
        """
        self.db.table = 'events'
        return self.db.select_all_from_table_by_key_value(SPORT, sport_name)

    def disable_selection(self):
        """
        Function to disable a selection and update parent event if all selections inactive
        """
        self.db.table = 'selections'
        name = self.all_args.get('name')
        outcome = self.all_args.get('outcome', 1)
        self.db.update_row({'active': 0, 'outcome': outcome}, 'name', name)
        event_name = self.db.select_all_from_table_by_key_value('name', name)[0].get(EVENT)
        selections = self.get_all_selections_by_event(event_name)
        if not any([selection.get('active') for selection in selections]):
            self.all_args['name'] = event_name
            self.disable_event()

    def disable_all_selections_by_event(self, event_name):
        """
        Function to disable all selections of an event

        :param event_name: Name of the parent event
        :type event_name: str
        """
        self.db.table = 'selections'
        outcome = 1
        self.db.update_row({'active': 0, 'outcome': outcome}, EVENT, event_name)

    def get_all_selections_by_event(self, event_name):
        """
        Function to fetch all selections of an event

        :param event_name: Name of the parent event
        :type event_name: str

        :return: List of matching selections
        :rtype: list
        """
        self.db.table = 'selections'
        return self.db.select_all_from_table_by_key_value(EVENT, event_name)

    def create_activity(self):
        """
        Function to create an activity

        """
        name = self.all_args.get('name', '')
        slug = slugify(name)
        if self.activity_type == SELECTION:
            self.db.table = 'selections'
            price = "{:.2f}".format(float(self.all_args.get('price', '0.00')))
            self.db.insert_into_table(
                ['name', 'active', 'price', 'event'],
                [(name, 1, price, self.all_args.get('event'))])
        elif self.activity_type == EVENT:
            self.db.table = 'events'
            ts = f"{self.all_args.get('scheduled_start', '2021/10/15, 19:30:39')}+00:00"
            scheduled_start = datetime.strptime(ts, "%Y/%m/%d, %H:%M:%S%z").isoformat()
            self.db.insert_into_table(
                ['name', 'slug', 'active', 'scheduled_start', 'sport'],
                [(name, slug, 1, scheduled_start, self.all_args.get('sport'))])
        else:
            self.db.table = 'sports'
            self.db.insert_into_table(['name', 'slug', 'active'], [(name, slug, 1)])

    def delete_activity(self):
        """
        Function to delete an activity
        """
        if self.activity_type == SELECTION:
            self.db.table = 'selections'
            selection_name = self.all_args.get('name')
            self.db.delete_row('name', selection_name)
        elif self.activity_type == EVENT:
            event_name = self.all_args.get('name')
            self.delete_selections_by_event(event_name)
            self.db.table = 'events'
            self.db.delete_row('name', event_name)
        else:
            sport_name = self.all_args.get('name')
            events = self.get_all_events_by_sport(sport_name)
            for event in events:
                event_name = event.get('name')
                self.delete_selections_by_event(event_name)
                self.db.table = 'events'
                self.db.delete_row('name', event_name)
            self.db.table = 'sports'
            self.db.delete_row('name', sport_name)

    def delete_selections_by_event(self, event_name):
        """
        Function to delete selections of an event

        :param event_name: Name of the parent event
        :type event_name: str
        """
        self.db.table = 'selections'
        selections = self.get_all_selections_by_event(event_name)
        for selection in selections:
            selection_name = selection.get('name')
            self.db.delete_row('name', selection_name)
