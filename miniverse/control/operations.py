from miniverse.model.exceptions import NotEnoughMoneyException, AsymmetricTransferException
from miniverse.model.model import User, Transaction, Transfer, TransactionType, TransferType
from miniverse.model.schemas import UserSchema, TransactionSchema, TransferSchema
from miniverse.service.urldefines import USER_GET_URI, TRANSACTION_GET_URI, TRANSFER_GET_URI


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


def create_transaction(session, user_uri, amount, transaction_type, commit=True):
    """
    Registers a new money transaction in the DB.
    Checks if the transaction is coherent with the user funds.
    Only commits if 'commit' is set to true. This allows us to completely rollback
    transfers.
    """
    # Check parameters
    if transaction_type not in TransactionType.all_values():
        raise ValueError(transaction_type + " is not a proper TransactionType.")

    if amount == 0:
        raise ValueError("If no money is moved, this is not a money transaction!")

    # First we get the user id
    user_id = user_uri.split("/")[-1]

    # Perform a security check
    if amount < 0:
        check_user_has_enough_money(session, user_id, amount)

    # Create the resource
    transaction = Transaction(user_phone=user_id, amount=amount, type=transaction_type)
    session.add(transaction)
    session.flush()
    transaction_id = transaction.id

    # Update user's funds
    update_user_funds(session, user_id, amount)

    # And go go go!
    if commit:
        session.commit()
    return TRANSACTION_GET_URI.format(transaction_id=transaction_id)


def get_transaction(session, transaction_id, expand=False):
    """
    Returns a money transaction stored in the DB
    """
    transaction = session.query(Transaction).get(transaction_id)
    transaction_schema = TransactionSchema()
    transaction_json = transaction_schema.dump(transaction).data
    # We may want to expand the user
    if expand:
        user_id = transaction_json["user"].split("/")[-1]
        user_json = get_user(session, user_id)
        transaction_json["user"] = user_json
    return transaction_json


def get_user_transactions(session, user_id, expand=False):
    """
    Returns all the transactions a user has performed.
    """
    if expand:
        result = session.query(Transaction).filter(Transaction.user_phone == user_id).all()
        transaction_schema = TransactionSchema()
        transactions = [transaction_schema.dump(r).data for r in result]
    else:
        result = session.query(Transaction.id).filter(Transaction.user_phone == user_id).all()
        transactions = [TRANSACTION_GET_URI.format(transaction_id=r.id) for r in result]
    return transactions


def check_transfer_is_symmetric(session, withdrawal_id, deposit_id):
    """
    Makes a couple of tests over the moved quantities.
    """
    w = get_transaction(session, withdrawal_id)
    d = get_transaction(session, deposit_id)
    if w["amount"] > 0:
        raise ValueError("The withdrawn amount must be negative.")

    if w["amount"] != -d["amount"]:
        raise AsymmetricTransferException("In a transfer, the withdrawn amount and deposited amount must have same absolute value.")


def create_transfer(session, withdrawal_uri, deposit_uri, comment, transfer_type):
    """
    Adds a transfer to the database. The transactions have already been created.
    """
    # Check parameter
    if transfer_type not in TransferType.all_values():
        raise ValueError(transfer_type + " is not a proper TransferType.")

    # Get the transaction ids
    withdrawal_id = int(withdrawal_uri.split("/")[-1])
    deposit_id = int(deposit_uri.split("/")[-1])

    # Check transfer is symmetric
    check_transfer_is_symmetric(session, withdrawal_id, deposit_id)

    # Store the transfer and commit transactions and transfer
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
    return an "expanded" dict with transaction data instead of resource uris
    if 'expand' is true.
    """
    transfer = session.query(Transfer).get(transfer_id)
    transfer_schema = TransferSchema()
    transfer_json = transfer_schema.dump(transfer).data

    # If we want to expand the transactions
    if expand:
        withdrawal_id = int(transfer_json["withdrawal"].split("/")[-1])
        deposit_id = int(transfer_json["deposit"].split("/")[-1])
        withdrawal_json = get_transaction(session, withdrawal_id)
        deposit_json = get_transaction(session, deposit_id)
        transfer_json["withdrawal"] = withdrawal_json
        transfer_json["deposit"] = deposit_json

    return transfer_json

