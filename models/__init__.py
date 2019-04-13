from .base_models import *
from .models import *

db = SqliteDatabase('database.sqlite')
db.connect()
db.create_tables([User, Match])
