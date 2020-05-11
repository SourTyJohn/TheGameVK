import sqlalchemy as sql
from data.db_session import SqlAlchemyBase


class Battle(SqlAlchemyBase):
    __tablename__ = 'battles'

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
