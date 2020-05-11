import sqlalchemy as sql
from data.db_session import SqlAlchemyBase

from data.gameEngine.contents.items import *

ID_PREFIX = [None, 'i_', 'w_', 't_']
ITEM_TYPES = [None, 'Предмет', 'Оружие', 'Тринкет']

"""Все классы предметов из модулей contents. Заполняется с запуском main.py"""
ITEMS = {}


class Item(SqlAlchemyBase):
    __tablename__ = 'items'

    id = sql.Column(sql.String, primary_key=True)
    item_type = sql.Column(sql.Integer, nullable=False)  # 1 - item, 2 - weapon, 3 - trinket

    name = sql.Column(sql.String, default='?ItemName?')
    rarity = sql.Column(sql.Integer, default=0)

    def __init__(self, item_class):
        self.name, self.rarity, self.item_type, self.id = item_class.set()
        ITEMS[self.id] = item_class


def init_items(session):
    session.query(Item).delete()
    session.add_all([
        Item(i_Bread),
        Item(i_PoisonBottle)
    ])
    session.commit()
    session.close()


def show_item(item_id, session, full=False):
    item = id_to_class(item_id)

    if full:
        description = f'{item.name} - {ITEM_TYPES[item.item_type]}'
        for string in item.description:
            description += f'\n{string}\n'

        # price
        buy, sell = 0, 0
        description += f'Продажа: {buy}з.    Покупка: {sell}з.'

    else:
        description = f'({item_id}) {item.name}'

    return description


def show_inventory(inventory: dict, session, inv_filter=None):
    result = ''

    for i, x in enumerate(inventory.keys()):
        if inv_filter is not None:
            pass

        result += f'{i + 1}. {show_item(x, session)}: {inventory[x]}шт.\n'

    return result, len(inventory.keys())


def id_to_class(item_id):
    return ITEMS[item_id]
