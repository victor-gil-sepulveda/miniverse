from miniverse.model.exceptions import NotEnoughMoneyException, AsymmetricTransferException
from miniverse.model.model import User, Movement, Transfer, MovementType, TransferType
from miniverse.model.schemas import UserSchema, MovementSchema, TransferSchema
from miniverse.service.urldefines import USER_GET_URI, MOVEMENT_GET_URI, TRANSFER_GET_URI


def create_user(session, phone_number, name, pass_hash, funds=0.0):
    """
    Inserts a new user/player in the DB.
    """
    # Perform the db job
    user = User(phone_number=phone_number, name=name, pass_hash=pass_hash, funds=funds)
    session.add(user)
    session.commit()
    return USER_GET_URI.format(user_id=phone_number)


def get_user(session, user_id):
    """
    Gets a user with id = name from the database. Returns a json.
    """
    user = session.query(User).get(user_id)
    user_schema = UserSchema()
    user_json = user_schema.dump(user).data
    return user_json


def get_user_balance(session, user_id):
    """
    Gets the funds of a user with user_id = name
    """
    balance = session.query(User.funds).filter(User.phone_number == user_id).all()
    return balance[0][0]


def check_user_has_enough_money(session, user_id, amount):
    """
    Checks that we can subtract 'amount' and still have funds. If not, an
    exception is raised. 'amount' is usually a negative number.
    """
    user_funds = get_user_balance(session, user_id)
    if user_funds + amount < 0:
        raise NotEnoughMoneyException("Not enough money in your wallet!")


def update_user_funds(session, user_id, amount):
    """
    Changes user funds by the given quantity 'amount'
    """
    session.query(User).filter_by(phone_number=user_id).update({'funds': User.funds + amount})


def create_movement(session, user_uri, amount, movement_type, commit=True):
    """
    Registers a new money movement in the DB.
    Checks if the movement is coherent with the user funds.
    Only commits if 'commit' is set to true. This allows us to completely rollback
    transfers.
    """
    # Check parameters
    if movement_type not in MovementType.all_values():
        raise ValueError(movement_type + " is not a proper MovementType.")

    if amount == 0:
        raise ValueError("If no money is moved, this is not a money movement!")

    # First we get the user id
    user_id = user_uri.split("/")[-1]

    # Perform a security check
    if amount < 0:
        check_user_has_enough_money(session, user_id, amount)

    # Create the resource
    movement = Movement(user_phone=user_id, amount=amount, type=movement_type)
    session.add(movement)
    session.flush()
    movement_id = movement.id

    # Update user's funds
    update_user_funds(session, user_id, amount)

    # And go go go!
    if commit:
        session.commit()
    return MOVEMENT_GET_URI.format(movement_id=movement_id)


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


def check_transfer_is_symetric(session, withdrawal_id, deposit_id):
    """
    Makes a couple of tests over the moved quantities.
    """
    w = get_movement(session, withdrawal_id)
    d = get_movement(session, deposit_id)
    if w["amount"] > 0:
        raise ValueError("The withdrawn amount must be negative.")

    if w["amount"] != -d["amount"]:
        raise AsymmetricTransferException("In a transfer, the withdrawn amount and deposited amount must have same absolute value.")



def create_transfer(session, withdrawal_uri, deposit_uri, comment, transfer_type):
    """
    Adds a transfer to the database. The movements have already been created.
    """
    # Check parameter
    if transfer_type not in TransferType.all_values():
        raise ValueError(transfer_type + " is not a proper TransferType.")

    # Get the movement ids
    withdrawal_id = int(withdrawal_uri.split("/")[-1])
    deposit_id = int(deposit_uri.split("/")[-1])

    # Check transfer is symmetric
    check_transfer_is_symetric(session, withdrawal_id, deposit_id)

    # Store the transfer and commit movements and transfer
    transfer = Transfer(withdrawal_id=withdrawal_id,
                        deposit_id=deposit_id,
                        comment=comment,
                        type=transfer_type)

    session.add(transfer)
    session.flush()
    transfer_id = transfer.id
    session.commit()
    return TRANSFER_GET_URI.format(transfer_id=transfer_id)


def get_transfer(session, transfer_id, expand=False):
    """
    Obtains a transfer from the DB and serializes it to a dict. It will
    return an "expanded" dict with movement data instead of resource uris
    if 'expand' is true.
    """
    transfer = session.query(Transfer).get(transfer_id)
    transfer_schema = TransferSchema()
    transfer_json = transfer_schema.dump(transfer).data

    # If we want to expand the movements
    if expand:
        withdrawal_id = int(transfer_json["withdrawal"].split("/")[-1])
        deposit_id = int(transfer_json["deposit"].split("/")[-1])
        withdrawal_json = get_movement(session, withdrawal_id)
        deposit_json = get_movement(session, deposit_id)
        transfer_json["withdrawal"] = withdrawal_json
        transfer_json["deposit"] = deposit_json

    return transfer_json

