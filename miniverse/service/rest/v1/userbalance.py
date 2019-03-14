from flask import jsonify, make_response
from flask_api import status
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from miniverse.control.operations import get_user_balance
from miniverse.model.sessionsingleton import DbSessionHolder
from miniverse.service.urldefines import USER_GET_URI


class UserBalance(Resource):

    def __init__(self):
        pass

    def get(self, user_id):
        """
        Gets the balance of a given user
        """
        session = DbSessionHolder().get_session()
        try:
            balance = get_user_balance(session, user_id)
            balance_json = {
                "balance": balance,
                "user": USER_GET_URI.format(user_id=user_id)
            }

            response = make_response(jsonify(balance_json),
                                     status.HTTP_201_CREATED)
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
            session.rollback()
            return make_response(jsonify({"error": str(e)}),
                                 status.HTTP_500_INTERNAL_SERVER_ERROR)