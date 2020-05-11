import sqlalchemy as sql
from data.db_session import SqlAlchemyBase
from ._activeHeroes import ActiveHero
from data.gameEngine.entities.character import PassiveCharacter


#  Эта таблица хранит все параметры героев, которые в данный не на вылазке
class PassiveHero(SqlAlchemyBase, PassiveCharacter):
    __tablename__ = 'p_heroes'
    hero_id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)

    def __init__(self, name, level=9):
        self.name = name
        self.lvl = level
        self.s_free = level
        self.s_free_perks = level // 10

    def create_active(self):
        return ActiveHero(self)
