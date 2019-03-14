from flask import jsonify, make_response, request
from flask_api import status
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from miniverse.control.operations import create_transfer, get_transaction, create_transaction
from miniverse.model.exceptions import NotEnoughMoneyException
from miniverse.model.model import TransactionType
from miniverse.model.sessionsingleton import DbSessionHolder


class Transfer(Resource):

    def __init__(self):
        pass

    def post(self):
        """
        Creates a money transaction.
        """
        json_data = request.get_json(force=True)
        session = DbSessionHolder().get_session()

        try:

            withdrawal_uri = create_transaction(
                session,
                json_data["sender"],
                -int(json_data["amount"]),
                TransactionType.TRANSFER_WITHDRAWAL,
                commit=False
            )

            deposit_uri = create_transaction(
                session,
                json_data["receiver"],
                int(json_data["amount"]),
                TransactionType.TRANSFER_DEPOSIT,
                commit=False
            )

            transfer_uri = create_transfer(
                session,
                withdrawal_uri,
                deposit_uri,
                json_data["comment"],
                json_data["type"]
            )

            response = make_response(jsonify(json_data),
                                     status.HTTP_201_CREATED)
            response.headers["location"] = transfer_uri
            response.autocorrect_location_header = False
            return response

        except (KeyError, ValueError, NotEnoughMoneyException), e:
            return make_response(jsonify({"error": str(e)}),
                                 status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            session.rollback()
            return make_response(jsonify({"error": "Something weird happened in the DB"}),
                                 status.HTTP_409_CONFLICT)
        except Exception, e:
            session.rollback()
            return make_response(jsonify({"error": str(e)}),
                                 status.HTTP_500_INTERNAL_SERVER_ERROR)
