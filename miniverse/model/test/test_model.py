import inspect
import json
import os
import unittest
import os.path
import datetime

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
import miniverse.model.test as test_module
from miniverse.model.model import Base, User, Movement, MovementType, TransferType, Transfer
from miniverse.model.schemas import UserSchema, MovementSchema, TransferSchema


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
        john = User(name="john",
                    pass_hash="96D9632F363564CC3032521409CF22A852F2032EEC099ED5967C0D000CEC607A",
                    created=datetime.datetime.strptime('24052010', "%d%m%Y").date())
        susan = User(name="susan",
                     pass_hash="B78469618FB15871B9508DEFD1FF70014747C1F918E4185425C5F2BBEA2A4E5D",
                     created=datetime.datetime.strptime('24052010', "%d%m%Y").date())

        movement1 = Movement(user=john, type=MovementType.CARD_WITHDRAWAL, amount=-10.0)
        movement2 = Movement(user=susan, type=MovementType.TRANSFER_WITHDRAWAL, amount=-5.0)
        movement3 = Movement(user=susan, type=MovementType.TRANSFER_DEPOSIT, amount=5.0)

        transfer = Transfer(withdrawal=movement2,
                            deposit=movement3,
                            comment="That was a great dinner!!",
                            type=TransferType.PUBLIC)

        session.add_all([
            john, susan,
            movement1, movement2, movement3,
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

        movement_schema = MovementSchema()
        for b in self.session.query(Movement).all():
            data.append(movement_schema.dump(b).data)

        transfer_schema = TransferSchema()
        for b in self.session.query(Transfer).all():
            data.append(transfer_schema.dump(b).data)

        print json.dumps(data, indent=4, sort_keys=True)

        # # fp = open(os.path.join(self.data_folder, "loaded_data.json"), "w")
        # # json.dump(data, fp=fp, indent=4, sort_keys=True)
        #
        # fp = open(os.path.join(self.data_folder, "loaded_data.json"), "r")
        # expected = json.load(fp)
        # self.maxDiff = None
        # self.assertItemsEqual(data, expected)

if __name__ == '__main__':
    unittest.main()