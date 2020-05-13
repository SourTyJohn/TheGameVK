import sqlalchemy as sql
from data.db_session import SqlAlchemyBase
import sqlalchemy.orm as orm
from data.gameEngine.entities.character import ActiveCharacter
from sqlalchemy.orm import relation


#  Эта таблица хранит все параметры героев, которые в данный момент на вылазке
class ActiveHero(SqlAlchemyBase, ActiveCharacter):
    __tablename__ = 'a_heroes'
    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)

    passive_id = sql.Column(sql.Integer, sql.ForeignKey('p_heroes.id'), nullable=True)
    passive = orm.relation('PassiveHero')

    weapon = sql.Column(sql.String, sql.ForeignKey("items.id"))
    w = relation("Item")

    def __init__(self, p_hero, session):
        self.passive_id = p_hero.id
        self.passive = p_hero
        session.commit()
        self.start()

    def __repr__(self):
        res = f':: {self.passive.name}. Уровень: {self.passive.lvl}\n'
        if self.weapon:
            res += f'Оружие: {self.w.name}'
        return res

    def exit(self, session):
        session.delete(self)
        session.flush()
