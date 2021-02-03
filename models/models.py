import datetime

from peewee import CharField, DateTimeField, ForeignKeyField, IntegerField

from models import BaseModel


class User(BaseModel):
    username = CharField()
    telegram_id = IntegerField(unique=True)


class Match(BaseModel):
    first_opponent_user_id = ForeignKeyField(User, backref="matches")
    second_opponent_user_id = ForeignKeyField(User, backref="matches")
    created_date = DateTimeField(default=datetime.datetime.now)
    first_opponent_score = IntegerField()
    second_opponent_score = IntegerField()
