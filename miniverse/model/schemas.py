from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from miniverse.model.model import User, Movement
from miniverse.service.urldefines import USER_GET_URL


class UserUri(fields.Field):
    def _serialize(self, user_id, attr, obj, **kwargs):
        return USER_GET_URL.format(user_id=user_id)


class UserSchema(ModelSchema):
    class Meta:
        model = User


class MovementSchema(ModelSchema):
    user = UserUri(attribute="user_id", dump_only=True)

    class Meta:
        model = Movement


