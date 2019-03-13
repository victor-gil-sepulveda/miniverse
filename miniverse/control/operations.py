from sqlalchemy.sql.expression import select

from miniverse.model.model import User
from miniverse.model.schemas import UserSchema
from miniverse.service.urldefines import USER_GET_URL


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


def get_user_balance(session, name):
    """
    Gets the funds of a user with user_id = name
    """
    balance = session.query(User.funds).filter(User.name == name).all()
    return balance[0][0]


def create_movement():
    pass


def create_transfer():
    pass





def get_movement():
    pass


def get_transfer():
    pass

