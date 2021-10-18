# rest_app
 Basic python/flask/mysql/docker CRUD app
# Git clone

git clone https://github.com/andrew-phelan/rest_app.git

# Change directory

cd rest_app

# Build and Start container

docker-compose -f docker-compose.dev.yml up --build

# App running

web_1      |  * Running on all addresses.

web_1      |    WARNING: This is a development server. Do not use it in a production deployment.

web_1      |  * Running on http://172.18.0.3:5000/ (Press CTRL+C to quit)

Check the localhost address and update CURL commands below if required.

# View test data

curl -is 'http://172.18.0.3:5000/sports'

curl -is 'http://172.18.0.3:5000/sports' -X POST -H "Content-Type: application/json" -d '{"events":"false", "name":"Football"}'

curl -is 'http://172.18.0.3:5000/sports' -X POST -H "Content-Type: application/json" -d '{"events":"true", "name":"Football"}'

curl -is 'http://172.18.0.3:5000/events'

curl -is 'http://172.18.0.3:5000/events' -X POST -H "Content-Type: application/json" -d '{"selections":"true", "name":"World Cup 2022"}'

curl -is 'http://172.18.0.3:5000/events' -X POST -H "Content-Type: application/json" -d '{"name":"World Cup 2022"}'

curl -is 'http://172.18.0.3:5000/selections'

curl -is 'http://172.18.0.3:5000/selections' -X POST -H "Content-Type: application/json" -d '{"name":"Norway Win"}'

# Create new activities

curl -is 'http://172.18.0.3:5000/create' -X POST -H "Content-Type: application/json" -d '{"name":"horse racing"}'

curl -is 'http://172.18.0.3:5000/create' -X POST -H "Content-Type: application/json" -d '{"name":"2pm Race", "scheduled_start": "2021/10/16, 21:55:14", "sport": "horse racing"}'

curl -is 'http://172.18.0.3:5000/create' -X POST -H "Content-Type: application/json" -d '{"name":"No 10 Win", "price": "20.0001", "event":"2pm Race"}'

# Start an Event

curl -is 'http://172.18.0.3:5000/start' -X POST -H "Content-Type: application/json" -d '{"name":"2pm Race"}'

# Search

curl -is 'http://172.18.0.3:5000/search' -X POST -H "Content-Type: application/json" -d '{"filters":["0"], "regex": "^N"}'

curl -is 'http://172.18.0.3::5000/search' -X POST -H "Content-Type: application/json" -d '{"filters":["0", "1"], "regex": "^N"}'

# Deactivate by Sport

curl -is 'http://172.18.0.3:5000/inactive' -X POST -H "Content-Type: application/json" -d '{"name":"Football"}'

# Deactivate by Event
curl -is 'http://172.18.0.3:5000/inactive' -X POST -H "Content-Type: application/json" -d '{"name":"World Cup 2022", "status": 2}'

# Deactivate by Selection

curl -is 'http://172.18.0.3:5000/inactive' -X POST -H "Content-Type: application/json" -d '{"name":"Norway Win", "outcome": 3}'

# Delete Activities

curl -is 'http://172.18.0.3:5000/delete' -X POST -H "Content-Type: application/json" -d '{"name":"horse racing"}'

curl -is 'http://172.18.0.3:5000/delete' -X POST -H "Content-Type: application/json" -d '{"name":"2pm Race", "sport": "horse racing"}'

curl -is 'http://172.18.0.3:5000/delete' -X POST -H "Content-Type: application/json" -d '{"name":"No 10 Win", "event":"2pm Race"}'

# Stopping the APP

CTRL + C
