from marshmallow import Schema, fields, validate

class AIQuestionSchema(Schema):
    text = fields.String(
        required=True,
        validate=validate.Length(min=1, max=5000)
    )

    class Meta:
        unknown = "exclude"
