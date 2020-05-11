import sqlalchemy as sql
from data.db_session import SqlAlchemyBase
import sqlalchemy.orm as orm
from data.gameEngine.entities.character import ActiveCharacter


#  Эта таблица хранит все параметры героев, которые в данный момент на вылазке
class ActiveHero(SqlAlchemyBase, ActiveCharacter):
    __tablename__ = 'a_heroes'
    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)

    passive_id = sql.Column(sql.Integer, sql.ForeignKey('p_heroes.hero_id'), nullable=True)
    passive = orm.relation('PassiveHero')

    def __init__(self, p_hero):
        self.passive_id = p_hero.hero_id
        self.start()

    def exit(self, session):
        session.delete(self)
        session.flush()
