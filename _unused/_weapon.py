import sqlalchemy as sql
from data.db_session import SqlAlchemyBase, create_session


class Weapon(SqlAlchemyBase):
    __tablename__ = 'weapons'

    weapon_id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    weapon_type = sql.Column(sql.Integer, nullable=False)

    mod_1 = sql.Column(sql.Integer, nullable=True)
    mod_2 = sql.Column(sql.Integer, nullable=True)

    def __init__(self, weapon_type, mod_1, mod_2, id):
        self.weapon_id = id
        self.weapon_type = weapon_type
        self.mod_1, self.mod_2 = mod_1, mod_2

    """Проверяет, есть ли уже такое оружие в базе и если нет, то добавляет через __init__"""
    def smart_init(self, weapon_type, mod_1, mod_2, session: create_session()):
        id = f'w_{weapon_type}_{mod_1}_{mod_2}'
        if not session.query(Weapon).filter(Weapon.weapon_id == id).first():
            Weapon(weapon_type, mod_1, mod_2, id)

    def give(self, weapon_params, session, vk_id):
        pass
