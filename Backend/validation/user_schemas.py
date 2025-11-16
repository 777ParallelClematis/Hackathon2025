from marshmallow import Schema, fields, validate

class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        validate=validate.Length(min=6, max=128)
    )

    class Meta:
        unknown = "exclude"  # forbid extra fields


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

    class Meta:
        unknown = "exclude"
