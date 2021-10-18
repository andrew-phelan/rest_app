from collections import OrderedDict
from datetime import datetime, timezone

from .db import DBConnection

SPORTS_TABLE = "sports"
SPORTS_VALUES = "name VARCHAR(32) NOT NULL PRIMARY KEY, slug VARCHAR(32), active BOOLEAN NOT NULL"
EVENTS_TABLE = "events"
EVENTS_VALUES = ("name VARCHAR(32) NOT NULL PRIMARY KEY, slug VARCHAR(32), active BOOLEAN NOT NULL, "
                 "type INT DEFAULT 0, status INT DEFAULT 0, scheduled_start TIMESTAMP, "
                 "actual_start TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, sport VARCHAR(32), "
                 "FOREIGN KEY(sport) REFERENCES sports(name)")
SELECTIONS_TABLE = "selections"
SELECTIONS_VALUES = ("name VARCHAR(32) NOT NULL PRIMARY KEY, active BOOLEAN NOT NULL, "
                     "price DECIMAL(10,2) DEFAULT 0.00, outcome INT DEFAULT 0, "
                     "event VARCHAR(32), FOREIGN KEY(event) REFERENCES events(name)")
SETUP_CMDS = OrderedDict([
    (SPORTS_TABLE, SPORTS_VALUES), (EVENTS_TABLE, EVENTS_VALUES), (SELECTIONS_TABLE, SELECTIONS_VALUES)])


def setup_db(database_name):
    """
    Function to setup the required database, tables and add some test data

    :param database_name: Name of the DB to be created
    :type database_name: str
    """
    connection = DBConnection(database_name)
    try:
        connection.drop_database()
    except Exception as e:
        print(str(e))
        pass
    connection.create_database()
    for key, value in SETUP_CMDS.items():
        connection.table = key
        connection.create_table(value)
        if key == "sports":
            connection.insert_into_table(['name', 'slug', 'active'], [('Football', 'football', 1)])
        elif key == "events":
            scheduled_start = datetime.now(timezone.utc).isoformat()
            connection.insert_into_table(
                ['name', 'slug', 'active', 'scheduled_start', 'sport'],
                [('World Cup 2022', 'world-cup', 1, scheduled_start, 'Football')])
        else:
            connection.insert_into_table(
                ['name', 'active', 'price', 'event'],
                [('Norway Win', 1, float(f"{10.000:.2f}"), 'World Cup 2022')])
