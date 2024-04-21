import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class Password(SqlAlchemyBase, UserMixin):
    __tablename__ = 'passwords'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    isOpen = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
