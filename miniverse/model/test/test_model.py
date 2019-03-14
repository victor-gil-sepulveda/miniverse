import inspect
import json
import os
import unittest
import os.path
import datetime
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
import miniverse.model.test as test_module
from miniverse.model.model import Base, User, Transaction, TransactionType, TransferType, Transfer, CreditCard, \
    CreditCardTransaction, CreditCardStatus
from miniverse.model.schemas import UserSchema, TransactionSchema, TransferSchema, CreditCardTransactionSchema, \
    CreditCardSchema


class TestModel(unittest.TestCase):
    TEST_DB = 'test_miniverse_model.db'

    @classmethod
    def setUpClass(cls):
        # get test data folder
        cls.data_folder = os.path.join(os.path.dirname(inspect.getfile(test_module)), "data")

    def setUp(self):
        # Populate the DB
        if os.path.exists(TestModel.TEST_DB):
            os.remove(TestModel.TEST_DB)
        engine = create_engine('sqlite:///'+TestModel.TEST_DB)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        ## Users
        john = User(phone_number="+41569882599",
                    name="john",
                    pass_hash="96D9632F363564CC3032521409CF22A852F2032EEC099ED5967C0D000CEC607A",
                    created=datetime.datetime.strptime('24052010', "%d%m%Y").date())
        susan = User(phone_number="+34615829532",
                     name="susan",
                     pass_hash="B78469618FB15871B9508DEFD1FF70014747C1F918E4185425C5F2BBEA2A4E5D",
                     created=datetime.datetime.strptime('24052010', "%d%m%Y").date())

        # John pays the dinner (10 eu)
        john_card = CreditCard(user=john,
                               number="4929867030624094",
                               status=CreditCardStatus.ACTIVE) # yeha! a Visa cc!
        cc_transaction = CreditCardTransaction(card=john_card, amount=-10)

        # But they share expenses :) (5 and 5 eu!)
        transaction1 = Transaction(user=susan, type=TransactionType.TRANSFER_WITHDRAWAL, amount=-5.0,
                             created=datetime.datetime.strptime('24052010', "%d%m%Y").date())
        transaction2 = Transaction(user=john, type=TransactionType.TRANSFER_DEPOSIT, amount=5.0,
                             created=datetime.datetime.strptime('24052010', "%d%m%Y").date())
        transfer = Transfer(withdrawal=transaction1,
                            deposit=transaction2,
                            comment="This is your half. That was a great dinner!!",
                            type=TransferType.PUBLIC,
                            created=datetime.datetime.strptime('24052010', "%d%m%Y").date())

        session.add_all([
            john, susan,
            transaction1, transaction2,
            cc_transaction,
            transfer
        ])
        session.commit()
        self.session = session

    def test_model_loaded(self):
        """
        Tests that we can create the model and serialize it (using
        """
        data = []

        user_schema = UserSchema()
        for b in self.session.query(User).all():
            data.append(user_schema.dump(b).data)

        transaction_schema = TransactionSchema()
        for b in self.session.query(Transaction).all():
            data.append(transaction_schema.dump(b).data)

        transfer_schema = TransferSchema()
        for b in self.session.query(Transfer).all():
            data.append(transfer_schema.dump(b).data)

        credit_card_schema = CreditCardSchema()
        for b in self.session.query(CreditCard).all():
            data.append(credit_card_schema.dump(b).data)

        cc_transaction_schema = CreditCardTransactionSchema()
        for b in self.session.query(CreditCardTransaction).all():
            data.append(cc_transaction_schema.dump(b).data)

        # fp = open(os.path.join(self.data_folder, "loaded_data.json"), "w")
        # json.dump(data, fp=fp, indent=4, sort_keys=True)

        fp = open(os.path.join(self.data_folder, "loaded_data.json"), "r")
        expected = json.load(fp)
        self.maxDiff = None
        self.assertItemsEqual(data, expected)

    def test_enums(self):
        self.assertItemsEqual(['PRIVATE', 'PUBLIC'], TransferType.all_values())
        self.assertIn("PUBLIC", TransferType.all_values())
        self.assertNotIn("NOT PUBLIC", TransferType.all_values())

if __name__ == '__main__':
    unittest.main()
