# validation/note_schemas.py
from marshmallow import Schema, fields, validate, EXCLUDE


class SaveNoteSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    note_text = fields.String(
        required=True,
        validate=validate.Length(min=1, max=10000)
    )
    title = fields.String(
        required=False,
        validate=validate.Length(max=255)
    )


class UpdateNoteSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    # Both fields optional, but at least one must be present
    note_text = fields.String(
        required=False,
        validate=validate.Length(min=1, max=10000)
    )
    title = fields.String(
        required=False,
        validate=validate.Length(max=255)
    )
