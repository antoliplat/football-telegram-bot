from peewee import Model, SqliteDatabase

db = SqliteDatabase('database.sqlite')


class BaseModel(Model):
    class Meta:
        database = db
