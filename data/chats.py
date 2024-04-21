import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class Chat(SqlAlchemyBase, UserMixin):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    userId = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    otherUserId = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
