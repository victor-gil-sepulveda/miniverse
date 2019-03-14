from flask import jsonify, make_response
from flask_api import status
from flask_restful import Resource
from miniverse.control.operations import get_user_movements
from miniverse.model.sessionsingleton import DbSessionHolder
from webargs import fields
from flask import request
from webargs.flaskparser import parser

get_args = {
    "expand": fields.Bool(missing=False, required=False)
}


class UserMovements(Resource):

    def __init__(self):
        pass

    def get(self, user_id):
        """
        Gets the balance of a given user
        """
        session = DbSessionHolder().get_session()
        args = parser.parse(get_args, request)

        try:
            movements = get_user_movements(session, user_id, expand=args["expand"])

            response = make_response(jsonify(movements),
                                     status.HTTP_201_CREATED)
            response.autocorrect_location_header = False
            return response

        except Exception, e:
            return make_response(jsonify({"error": str(e)}),
                                 status.HTTP_500_INTERNAL_SERVER_ERROR)
