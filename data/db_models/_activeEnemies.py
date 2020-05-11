import sqlalchemy as sql
from data.db_session import SqlAlchemyBase
from data.gameEngine.entities.character import ActiveCharacter
from data.gameEngine.contents.enemies import ENEMIES


class Enemy(SqlAlchemyBase, ActiveCharacter):
    __tablename__ = 'enemy'
    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)

    passive_id = sql.Column(sql.Integer, nullable=False)
    passive = sql.Column(sql.Integer, nullable=False)

    def __init__(self, enemy_type):
        self.passive = ENEMIES[enemy_type]
        self.start()
