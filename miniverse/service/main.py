from flask import Flask
from miniverse.model.sessionsingleton import DbSessionHolder
from miniverse.service.rest.api import setup_rest_api

DB_NAME = "miniverse_local.db"


def run_flask_server(host="0.0.0.0", port=5000, debug=False):
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
    DbSessionHolder(DB_NAME)

    # Init the REST API
    setup_rest_api(app)

    app.run(
        debug=debug,
        host=host,
        port=port,
        threaded=True #warning!
    )

if __name__ == "__main__":
    run_flask_server(debug=False)
