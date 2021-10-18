from flask import Flask, request, jsonify, abort

from lib.activities import Sport, Event, Selection
from lib.activity_mgr import ActivityMgr
from lib.db import DBConnection
from lib.db_setup import setup_db, SPORTS_TABLE, EVENTS_TABLE, SELECTIONS_TABLE

app = Flask(__name__)

DB_NAME = "application"
conn = DBConnection(DB_NAME, table=SPORTS_TABLE)
GET = 'GET'
POST = 'POST'
filter_one = "(t.name REGEXP '{0}') OR (t1.name REGEXP '{0}') OR (t2.name REGEXP '{0}')"
filter_two = "t1.scheduled_start >= now() - INTERVAL 24 HOUR"
filter_three = "t2.outcome= 3"
FILTERS = {0: filter_one, 1: filter_two, 2: filter_three}


class OperationNotPermittedException(Exception):
    pass


@app.before_first_request
def at_start_up(*args):
    """
    Start up function to create database objects
    """
    try:
        print(f"Creating database with: {args}")
        setup_db(DB_NAME)
    except Exception as e:
        print(f"Failed to set up database correctly. Error encountered: {str(e)}")


@app.route('/')
def home():
    """
    Route to GET to Index

    :raises HTTPException: 500 raised if POST request fails

    :return: 200 Response object
    :rtype: `requests.Response`
    """
    return "Index Page"


@app.route('/sports', methods=[GET, POST])
def get_sports():
    """
    Route to GET to Sports

    POST:
        - required:
            name: str
        - optional:
            events: bool

    :raises HTTPException: 500 raised if POST request fails

    :return: 200 Response object
    :rtype: `requests.Response`
    """
    conn.table = SPORTS_TABLE
    msg = "All Sports"
    try:
        if request.method == GET:
            result = [Sport(**sport).__dict__ for sport in conn.select_all_from_table()]
        else:
            data = request.get_json()
            event = True if data.get('events') == "true" else False
            name = data.get('name')
            if all([event, name]):
                conn.table = EVENTS_TABLE
                result = [Event(**event).__dict__ for event in conn.select_all_from_table_by_key_value('sport', name)]
                msg = f"All Events of {name}: "
            elif name:
                result = [Sport(**sport).__dict__ for sport in conn.select_all_from_table_by_key_value('name', name)]
                msg = f"Sport: {name}"
            else:
                msg, result = 'Invalid POST requirements.', data
        return jsonify({msg: result})
    except Exception as e:
        abort(500, f"Error fetching sport information:: {str(e)}")


@app.route('/events', methods=[GET, POST])
def get_events():
    """
    Route to GET to Events

    POST:
        - required:
            name: str
        - optional:
            selections: bool

    :raises HTTPException: 500 raised if POST request fails

    :return: 200 Response object
    :rtype: `requests.Response`
    """
    conn.table = EVENTS_TABLE
    msg = "All Events"
    try:
        if request.method == GET:
            result = [Event(**event).__dict__ for event in conn.select_all_from_table()]
        else:
            data = request.get_json()
            selections = True if data.get('selections') == "true" else False
            name = data.get('name')
            if all([selections, name]):
                conn.table = SELECTIONS_TABLE
                result = [Selection(**selection).__dict__ for selection in
                          conn.select_all_from_table_by_key_value('event', name)]
                msg = f"Selections for {name}: "
            elif name:
                result = [Event(**event).__dict__ for event in conn.select_all_from_table_by_key_value('name', name)]
                msg = f"Event: {name}"
            else:
                msg, result = 'Invalid POST requirements.', data
        return jsonify({msg: result})
    except Exception as e:
        abort(500, f"Error fetching event information:: {str(e)}")


@app.route('/selections', methods=[GET, POST])
def get_selections():
    """
    Route to GET to Selections

    POST:
        - required:
            name: str

    :raises HTTPException: 500 raised if POST request fails

    :return: 200 Response object
    :rtype: `requests.Response`
    """
    conn.table = SELECTIONS_TABLE
    msg = "All Selections"
    try:
        if request.method == GET:
            result = [Selection(**selection).__dict__ for selection in conn.select_all_from_table()]
        else:
            data = request.get_json()
            name = data.get('name')
            if name:
                result = [Selection(**selection).__dict__ for selection in
                          conn.select_all_from_table_by_key_value('name', name)]
                msg = f"Selection: {name}"
            else:
                msg, result = 'Invalid POST requirements.', data
        return jsonify({msg: result})
    except Exception as e:
        abort(500, f"Error fetching selection information:: {str(e)}")


@app.route('/create', methods=[POST])
def create_activity():
    """
    Route to POST new activity
    1) Sport
        - required:
            name: str
        -optional:
            slug: str
            active: bool
    2) Event
        - required:
            name: str
            sport: str
        - optional:
            slug: str
            active: bool
            scheduled_start: str
    3) Selection
        - required:
            name: str
            event: str
        - optional:
            active: bool
            price: str

    :raises HTTPException: 500 raised if POST request fails

    :return: 200 Response object
    :rtype: `requests.Response`
    """
    activity_type = None
    try:
        mgr = ActivityMgr(conn, **request.get_json())
        mgr.set_activity_type()
        activity_type = mgr.activity_type
        mgr.create_activity()
        return jsonify({'Success': f"{activity_type } Created."})
    except Exception as e:
        abort(500, f"Error creating {activity_type}:: {str(e)}")


@app.route('/start', methods=[POST])
def start_event():
    """
    Route to POST event start
    - required:
        name: str

    :raises HTTPException: 500 raised if POST request fails

    :return: 200 Response object
    :rtype: `requests.Response`
    """
    try:
        data = request.get_json()
        event_name = data.get('name')
        conn.table = EVENTS_TABLE
        conn.update_row({'status': 1, 'type': 1}, 'name', data.get('name'))
        return jsonify({"Success": f"{event_name } started."})
    except Exception as e:
        abort(500, f"Error starting event:: {str(e)}")


@app.route('/inactive', methods=[POST])
def disable_activity():
    """
    Route to POST disable activity
    1) Sport
        - required:
            name: str
    2) Event
        - required:
            name: str
        - optional:
            status: int
    3) Selection
        - required:
            name: str
        - optional:
            outcome: int

    :raises HTTPException: 500 raised if POST request fails

    :return: 200 Response object
    :rtype: `requests.Response`
    """
    activity_type = None
    try:
        mgr = ActivityMgr(conn, **request.get_json())
        mgr.set_activity_type()
        activity_type = mgr.activity_type
        mgr.end_activity()
        return jsonify({"Success": f"{activity_type } Inactive."})
    except Exception as e:
        abort(500, f"Error disabling {activity_type}:: {str(e)}")


@app.route('/delete', methods=[POST])
def delete_activity():
    """
    Route to POST delete activity
    - required:
        name: str

    :raises HTTPException: 500 raised if POST request fails

    :return: 200 Response object
    :rtype: `requests.Response`
    """
    activity_type = None
    try:
        mgr = ActivityMgr(conn, **request.get_json())
        mgr.set_activity_type()
        activity_type = mgr.activity_type
        mgr.delete_activity()
        return jsonify({"Success": f"{activity_type} Deleted."})
    except Exception as e:
        abort(500, f"Error deleting {activity_type}:: {str(e)}")


@app.route('/search', methods=[POST])
def search_activity():
    """
    Route to POST search activities
    - optional:
        regex: str
        filters: list
        expression: str

    :raises HTTPException: 500 raised if POST request fails

    :return: 200 Response object
    :rtype: `requests.Response`
    """
    query = None
    try:
        data = request.get_json()
        regex = data.get('regex', '^N')
        query = data.get('search_term', "")
        req_filters = data.get('filters', [])
        restricted = ["drop", "delete"]
        if any(val in query.lower() for val in restricted) or any(val in regex.lower() for val in restricted):
            raise OperationNotPermittedException(f"Restricted keywords found, search not permitted")
        if req_filters:
            query = query_builder(regex, req_filters, query)
        result = conn.execute_query(query, database=conn.database, result_req=True)
        return jsonify({"Filter results": result})
    except Exception as e:
        abort(500, f"Error Searching with Query {query}:: {str(e)}")


def query_builder(regex, filters, expression):
    """
    Function to build the search query

    :param regex: Regex pattern string
    :type regex: str
    :param filters: List of filters to be selected
    :type filters: list
    :param expression: MySQL expression to query
    :type expression: str

    :raises RuntimeError: raised is the search criteria produces None
    :return: Query built
    :rtype: str
    """
    base_query = "select t.name, t1.name, t2.name from sports t, events t1, selections t2 WHERE"
    selected_filters = []
    if expression:
        selected_filters = [expression]
    filters = [int(_) for _ in filters]
    for _ in filters:
        if not _:
            selected_filter = FILTERS.get(_).format(regex)
            selected_filters.append(selected_filter)
            continue
        selected_filters.append(FILTERS.get(_))
    if not selected_filters:
        raise RuntimeError("No matching search criteria found.")
    if len(selected_filters) == 1:
        return f"{base_query} {selected_filters[0]}"
    query = ""
    for index, _ in enumerate(selected_filters):
        if not index:
            query = "{0} {1}".format(base_query, _)
        query += " AND {0}".format(_)
    return query


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
