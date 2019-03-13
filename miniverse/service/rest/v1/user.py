from flask import jsonify, make_response, request
from flask_api import status
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from miniverse.control.operations import create_user
from miniverse.model.sessionsingleton import DbSessionHolder


class User(Resource):

    def __init__(self):
        pass

    def post(self):
        """
        Creates a new user.
        """
        json_data = request.get_json(force=True)
        session = DbSessionHolder().get_session()

        try:
            user_uri = create_user(session,
                                   json_data["phone_number"],
                                   json_data["name"],
                                   json_data["pass_hash"])
            response = make_response(jsonify(json_data),
                                     status.HTTP_201_CREATED)
            response.headers["location"] = user_uri
            response.autocorrect_location_header = False
            return response

        except KeyError, e:
            return make_response(jsonify({"error": str(e)}),
                                 status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            session.rollback()
            return make_response(jsonify({"error": "This phone is already in use :( "}),
                                 status.HTTP_409_CONFLICT)
        except Exception, e:
            session.rollback() # jsut in case
            return make_response(jsonify({"error": str(e)}),
                                 status.HTTP_500_INTERNAL_SERVER_ERROR)