from db import get_db

db = get_db()
users = db.users  # this references the "users" collection
