import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import relationship

Base = declarative_base()


class CheckableEnum(object):
    @classmethod
    def all_values(cls):
        attrs = dir(cls)
        enum_vals = []
        for attr in attrs:
            if "__" not in attr and attr.isupper():
                enum_vals.append(attr)
        return enum_vals


class TransferType(CheckableEnum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class TransactionType(CheckableEnum):
    TRANSFER_DEPOSIT = "TRANSFER_DEPOSIT"
    TRANSFER_WITHDRAWAL = "TRANSFER_WITHDRAWAL"
    FUNDS_DEPOSIT = "FUNDS_DEPOSIT"
    FUNDS_WITHDRAWAL = "FUNDS_WITHDRAWAL"


class CreditCardStatus(CheckableEnum):
    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"


USER_TABLE = "user"
TRANSFER_TABLE = "transfer"
TRANSACTION_TABLE = "transaction"
CREDITCARD_TABLE = "creditcard"
CCTRANSACTION_TABLE = "creditcard_transaction"


class User(Base):
    __tablename__ = USER_TABLE
    phone_number = Column(String(32), primary_key=True)
    name = Column(String(32))
    pass_hash = Column(String(256), nullable=False)
    funds = Column(Float, default=0.0)
    picture_path = Column(String(256), nullable=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)


class CreditCard(Base):
    __tablename__ = CREDITCARD_TABLE
    number = Column(String(16), primary_key=True)
    issued = Column(DateTime, nullable=True)
    active_since = Column(DateTime, nullable=True)
    expiry = Column(DateTime, nullable=True)
    status = Column(String(16), default=CreditCardStatus.INACTIVE) # Enum(CreditCardStatus)
    user_phone = Column(String(32), ForeignKey(USER_TABLE + '.phone_number'))
    user = relationship("User", foreign_keys=[user_phone], backref="cards")


class CreditCardTransaction(Base):
    __tablename__ = CCTRANSACTION_TABLE
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    card_number = Column(String(16), ForeignKey(CREDITCARD_TABLE + '.number'))
    card = relationship("CreditCard", foreign_keys=[card_number])


class Transaction(Base):
    __tablename__ = TRANSACTION_TABLE
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    user_phone = Column(String(32), ForeignKey(USER_TABLE + '.phone_number'))
    user = relationship("User", foreign_keys=[user_phone])
    type = Column(String(32), nullable=False) # Enum(TransactionType)
    created = Column(DateTime, default=datetime.datetime.utcnow)


class Transfer(Base):
    __tablename__ = TRANSFER_TABLE
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Constraint users are not equal, and amounts are equal with opposed sign
    # and types are TRANSFER_DEPOSIT and TRANSFER_WITHDRAWAL
    withdrawal_id = Column(Integer, ForeignKey(TRANSACTION_TABLE + '.id'))
    withdrawal = relationship("Transaction", foreign_keys=[withdrawal_id])

    deposit_id = Column(Integer, ForeignKey(TRANSACTION_TABLE + '.id'))
    deposit = relationship("Transaction", foreign_keys=[deposit_id])

    # Transfer comment
    comment = Column(String(256), nullable=False)

    # The transfer visibility
    type = Column(String(16), nullable=False) #Enum(TransferType)

    # For tracking purposes
    created = Column(DateTime, default=datetime.datetime.utcnow)