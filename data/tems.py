import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class Tem(SqlAlchemyBase, UserMixin):
    __tablename__ = 'tems'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
