from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from miniverse.model.model import User, Transaction, Transfer, CreditCard, CreditCardTransaction
from miniverse.service.urldefines import USER_GET_URI, TRANSACTION_GET_URI, CREDIT_CARD_GET_URL


class UserUri(fields.Field):
    def _serialize(self, user_id, attr, obj, **kwargs):
        return USER_GET_URI.format(user_id=user_id)


class TransactionUri(fields.Field):
    def _serialize(self, transaction_id, attr, obj, **kwargs):
        return TRANSACTION_GET_URI.format(transaction_id=transaction_id)


class CardUri(fields.Field):
    def _serialize(self, card_number, attr, obj, **kwargs):
        return CREDIT_CARD_GET_URL.format(card_number=card_number)


class UserSchema(ModelSchema):
    class Meta:
        model = User
        exclude = ("cards",)


class TransactionSchema(ModelSchema):
    user = UserUri(attribute="user_phone", dump_only=True)

    class Meta:
        model = Transaction


class TransferSchema(ModelSchema):
    withdrawal = TransactionUri(attribute="withdrawal_id", dump_only=True)
    deposit = TransactionUri(attribute="deposit_id", dump_only=True)

    class Meta:
        model = Transfer


class CreditCardSchema(ModelSchema):
    user = UserUri(attribute="user_id", dump_only=True)

    class Meta:
        model = CreditCard


class CreditCardTransactionSchema(ModelSchema):
    card = CardUri(attribute="card_id", dump_only=True)

    class Meta:
        model = CreditCardTransaction
