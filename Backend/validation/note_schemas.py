from marshmallow import Schema, fields, validate

class SaveNoteSchema(Schema):
    title = fields.String(
        required=False,
        validate=validate.Length(max=200)
    )
    note_text = fields.String(
        required=True,
        validate=validate.Length(min=1, max=10000)
    )

    class Meta:
        unknown = "exclude"
