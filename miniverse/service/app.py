from flask import Flask
from miniverse.model.sessionsingleton import DbSessionHolder
from miniverse.service.rest.api import setup_rest_api

DB_NAME = "miniverse_local.db"
DEBUG = False
HOST = "0.0.0.0"
PORT = 5000
DBTYPE = 'sqlite:///'
DB_URL = DBTYPE + DB_NAME

# for mysql docker image
DB_URL = "mysql://user:password@db:32000/miniverse"

app = Flask(__name__) # create the application instance :)

app.config.from_object(__name__) # Load config

# Load default config and override config from an environment variable
app.config.update(dict(
    SECRET_KEY='super secret key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

#Init the DB Session
DbSessionHolder(DB_URL)

# Init the REST API
setup_rest_api(app)

if __name__ == "__main__":
    app.run(
        debug=DEBUG,
        host=HOST,
        port=PORT,
        threaded=True  #
    )
