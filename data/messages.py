import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class Message(SqlAlchemyBase, UserMixin):
    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    userId = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    chatId = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    dateTime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
