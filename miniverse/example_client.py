import json
import requests

from tabulate import tabulate

from miniverse.model.model import TransactionType, TransferType


def get_complete_endpoint(endpoint):
    complete_endpoint = "http://127.0.0.1:5000/miniverse/v1{endpoint}".format(endpoint=endpoint)
    return complete_endpoint


def get_balance(user_uri_list):
    return [[requests.get(get_complete_endpoint(user_uri+"/balance")).json()["balance"]
            for user_uri in user_uri_list]]


if __name__ == "__main__":

    #*******************************************
    # Create users
    # *******************************************
    finn = requests.post(get_complete_endpoint("/user"), data=json.dumps({
        "name": "Finn",
        "phone_number": "+3655076979",
        "pass_hash": "0117CDBFAF2E85202A463435665001B2EFB5082E7D89E0221246BAF0103BAA90"
    }))
    finn_uri = finn.headers["location"]

    jake = requests.post(get_complete_endpoint("/user"), data=json.dumps({
        "name": "Jake",
        "phone_number": "+353209127263",
        "pass_hash": "7C9E7C1494B2684AB7C19D6AFF737E460FA9E98D5A234DA1310C97DDF5691834"
    }))
    jake_uri = jake.headers["location"]

    iceking = requests.post(get_complete_endpoint("/user"), data=json.dumps({
        "name": "Ice King",
        "phone_number": "+3655902767",
        "pass_hash": "90E1A788B58BDE874DB1A7FD051A4999436E13324656713ADD0D252CF2A16BCA"
    }))
    iceking_uri = iceking.headers["location"]
    users = [finn_uri, jake_uri, iceking_uri]
    headers = ["Finn", "Jake", "Ice King"]

    print "\n- Initial state. Everybody is poor :(\n"
    print tabulate(get_balance(users), headers)

    #*******************************************
    # Add funds to the wallets of finn and jake
    # *******************************************
    requests.post(get_complete_endpoint("/transaction"), data=json.dumps({
        "user": finn_uri,
        "amount": 150.0,
        "type": TransactionType.FUNDS_DEPOSIT
    }))

    requests.post(get_complete_endpoint("/transaction"), data=json.dumps({
        "user": jake_uri,
        "amount": 60.0,
        "type": TransactionType.FUNDS_DEPOSIT
    }))
    print "\n- Funds have been added!\n"
    print tabulate(get_balance(users), headers)

    #*******************************************
    # Transfer money between our guys
    # ******************************************
    requests.post(get_complete_endpoint("/transfer"), data=json.dumps({
        "sender": finn_uri,
        "receiver": jake_uri,
        "amount": 40.0,
        "comment": "Tree house rent.",
        "type": TransferType.PUBLIC
    }))
    requests.post(get_complete_endpoint("/transfer"), data=json.dumps({
        "sender": finn_uri,
        "receiver": iceking_uri,
        "amount": 20.0,
        "comment": "Give it to Gunter please!",
        "type": TransferType.PRIVATE
    }))
    requests.post(get_complete_endpoint("/transfer"), data=json.dumps({
        "sender": jake_uri,
        "receiver": iceking_uri,
        "amount": 15.0,
        "comment": "Thanks for the new sword! <3",
        "type": TransferType.PUBLIC
    }))
    print "\n- Some transfers after ...\n"
    print tabulate(get_balance(users), headers)

    # *******************************************
    # Show the transactions
    # ******************************************
    for user_name, user_uri in zip(headers, users):
        print "\n- Transactions for {user_name}".format(user_name=user_name)
        partial_endpoint = user_uri+"/transactions?expand=true"
        endpoint = get_complete_endpoint(partial_endpoint)
        print "- Endpoint: ", partial_endpoint
        transactions = requests.get(endpoint).json()
        for transaction in transactions:
            # We use a workaround to get the user name, as the get endpoint is not defined :D
            print "\t ->", headers[users.index(transaction["user"])], "amount:", transaction["amount"], "type:", transaction["type"]



