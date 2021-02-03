from peewee import SqliteDatabase

from models.base_models import BaseModel  # noqa
from models.models import Match, User

db = SqliteDatabase("database.sqlite")
db.connect()
db.create_tables([User, Match])
