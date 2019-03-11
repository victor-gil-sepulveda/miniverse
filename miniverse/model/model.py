import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, Enum
import enum

from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Boolean

Base = declarative_base()


class TransferType(enum.IntEnum):
    PUBLIC = 1
    PRIVATE = 2


class MovementType(enum.IntEnum):
    TRANSFER_DEPOSIT = 1
    TRANSFER_WITHDRAWAL = 2
    FUNDS_DEPOSIT = 3
    CARD_WITHDRAWAL = 4


USER_TABLE = "user"
TRANSFER_TABLE = "transfer"
MOVEMENT_TABLE = "movement"


class User(Base):
    __tablename__ = USER_TABLE
    name = Column(String(32), primary_key=True)
    pass_hash = Column(String(256), nullable=False)
    funds = Column(Float, default=0.0)
    picture_path = Column(String(256), nullable=True)


class Movement(Base):
    __tablename__ = MOVEMENT_TABLE
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, default=0.0)
    user_id = Column(Integer, ForeignKey(USER_TABLE + '.name'))
    user = relationship("User", foreign_keys=[user_id])


class Transfer(Base):
    __tablename__ = TRANSFER_TABLE
    id = Column(Integer, primary_key=True)
    # constraint users are not equal, and amounts are equal with opposed sign
    # and types are TRANSFER_DEPOSIT and TRANSFER_WITHDRAWAL
    withdrawal_id = Column(Integer, ForeignKey(MOVEMENT_TABLE + '.id'))
    withdrawal = relationship("Movement", foreign_keys=[withdrawal_id])

    deposit_id = Column(Integer, ForeignKey(MOVEMENT_TABLE + '.id'))
    deposit = relationship("Movement", foreign_keys=[deposit_id])
