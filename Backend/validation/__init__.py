from flask import jsonify

def validate_json(schema, data):
    """
    Validates JSON input against a Marshmallow schema.
    Returns a Flask response if invalid, otherwise None.
    """
    errors = schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    return None
