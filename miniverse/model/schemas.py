from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from miniverse.model.model import User, Movement, Transfer, CreditCard, CreditCardMovement
from miniverse.service.urldefines import USER_GET_URL, MOVEMENT_GET_URL, CREDIT_CARD_GET_URL


class UserUri(fields.Field):
    def _serialize(self, user_id, attr, obj, **kwargs):
        return USER_GET_URL.format(user_id=user_id)


class MovementUri(fields.Field):
    def _serialize(self, movement_id, attr, obj, **kwargs):
        return MOVEMENT_GET_URL.format(movement_id=movement_id)


class CardUri(fields.Field):
    def _serialize(self, card_number, attr, obj, **kwargs):
        return CREDIT_CARD_GET_URL.format(card_number=card_number)


class UserSchema(ModelSchema):
    class Meta:
        model = User
        exclude = ("cards",)


class MovementSchema(ModelSchema):
    user = UserUri(attribute="user_id", dump_only=True)

    class Meta:
        model = Movement


class TransferSchema(ModelSchema):
    withdrawal = MovementUri(attribute="withdrawal_id", dump_only=True)
    deposit = MovementUri(attribute="deposit_id", dump_only=True)

    class Meta:
        model = Transfer


class CreditCardSchema(ModelSchema):
    user = UserUri(attribute="user_id", dump_only=True)

    class Meta:
        model = CreditCard


class CreditCardMovementSchema(ModelSchema):
    card = CardUri(attribute="card_id", dump_only=True)

    class Meta:
        model = CreditCardMovement
