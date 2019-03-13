from gi._gi import Transfer
from sqlalchemy.sql.expression import select

from miniverse.model.exceptions import NotEnoughMoneyException
from miniverse.model.model import User, Movement
from miniverse.model.schemas import UserSchema, MovementSchema
from miniverse.service.urldefines import USER_GET_URL, MOVEMENT_GET_URL


def create_user(session, name, pass_hash, funds=0.0):
    """
    Inserts a new user/player in the DB.
    """
    # Perform the db job
    user = User(name=name, pass_hash=pass_hash, funds=funds)
    session.add(user)
    session.commit()
    return USER_GET_URL.format(user_id=name)


def get_user(session, name):
    """
    Gets a user with id = name from the database. Returns a json.
    """
    user = session.query(User).get(name)
    user_schema = UserSchema()
    user_json = user_schema.dump(user).data
    return user_json


def get_user_balance(session, user_id):
    """
    Gets the funds of a user with user_id = name
    """
    balance = session.query(User.funds).filter(User.name == user_id).all()
    return balance[0][0]


def check_user_has_enough_money(session, user_id, amount):
    """
    Checks that we can subtract 'amount' and still have funds. If not, an
    exception is raised. 'amount' is usually a negative number.
    """
    user_funds = get_user_balance(session, user_id)
    print "user funds", user_funds
    if user_funds + amount < 0:
        raise NotEnoughMoneyException("Not enough money in your wallet!")


def update_user_funds(session, user_id, amount):
    """
    Changes user funds by the given quantity 'amount'
    """
    session.query(User).filter_by(name=user_id).update({'funds': User.funds + amount})


def create_movement(session, user_uri, amount, movement_type, commit=True):
    """
    Registers a new money movement in the DB.
    Checks if the movement is coherent with the user funds.
    Only commits if 'commit' is set to true. This allows us to completely rollback
    transfers.
    """
    # First we get the user id
    user_id = user_uri.split("/")[-1]

    # Perform a security check
    if amount < 0:
        check_user_has_enough_money(session, user_id, amount)

    # Create the resource
    movement = Movement(user_name=user_id, amount=amount, type=movement_type)
    session.add(movement)
    session.flush()
    movement_id = movement.id

    # Update user's funds
    update_user_funds(session, user_id, amount)

    # And go go go!
    if commit:
        session.commit()
    return MOVEMENT_GET_URL.format(movement_id=movement_id)


def get_movement(session, movement_id, expand=False):
    """
    Returns a money movement stored in the DB
    """
    movement = session.query(Movement).get(movement_id)
    movement_schema = MovementSchema()
    movement_json = movement_schema.dump(movement).data
    # We may want to expand the user
    if expand:
        user_id = movement_json["user"].split("/")[-1]
        user_json = get_user(session, user_id)
        movement_json["user"] = user_json
    return movement_json


def create_transfer(session, withdrawal_uri, deposit_uri, comment, type):
    # Get the movement ids
    withdrawal_id = int(withdrawal_uri.split("/")[-1])
    deposit_id = int(deposit_uri.split("/")[-1])
    transfer = Transfer(withdrawal_id=withdrawal_id,
                        deposit_id=deposit_id,
                        comment=comment,
                        type=type)


def get_transfer(session, transfer_id, expand=False):
    pass

