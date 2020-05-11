import sqlalchemy as sql
from data.db_session import SqlAlchemyBase
from ast import literal_eval

from data.db_models._marketLot import LotSell, LotBuy, COMMISSION, COMMISSION_TEXT

from core import server


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    vk_id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)

    hero_1 = sql.Column(sql.Integer, sql.ForeignKey('a_heroes.id'), nullable=True)
    hero_2 = sql.Column(sql.Integer, sql.ForeignKey('a_heroes.id'), nullable=True)
    hero_3 = sql.Column(sql.Integer, sql.ForeignKey('a_heroes.id'), nullable=True)

    idle_heroes = sql.Column(sql.String, nullable=True)  # {passiveHero.id};{passiveHero.id};...
    good_inventory = sql.Column(sql.String, default='{}')  # dict {"item_id": count}
    temp_inventory = sql.Column(sql.String, default='{}')
    """temp_inventory - походный инвентарь. 
       Если Ваша кампания провалится, то Вы потеряете весь этот инвентарь
       good_inventory - инвентарь к которому нет доступа в походе,
       но он не теряется при провале """

    money = sql.Column(sql.Integer, default=1000)

    battle = sql.Column(sql.Integer, sql.ForeignKey('battles.id'), nullable=True)
    """ID сражения в котором участвует игрок"""

    keyboard = sql.Column(sql.SmallInteger, default=1)
    prev_keyboard = sql.Column(sql.Integer, default=1)
    page = sql.Column(sql.Integer, default=0)

    search = sql.Column(sql.String, nullable=True)
    sorting = sql.Column(sql.SmallInteger, default=0)

    selected_slot = sql.Column(sql.Integer, nullable=True)

    def __init__(self, vk_id):
        self.vk_id = vk_id
        self.hero_1, self.hero_2, self.hero_3 = None, None, None
        self.keyboard = 2
        self.idle_heroes = None

    def good_inventory_dict(self) -> dict:
        return literal_eval(self.good_inventory)

    def temp_inventory_dict(self) -> dict:
        return literal_eval(self.temp_inventory)

    """Переносит все вещи из походного в настоящий инвентарь. 
    Вызывается после успешного возврата с вылазки"""
    def temp_into_good(self):
        tmp = self.temp_inventory_dict()
        gdd = self.good_inventory_dict()

        for x in tmp.keys():
            if x in gdd.keys():
                gdd[x] += tmp[x]
            else:
                gdd[x] = tmp[x]

        self.good_inventory = str(gdd)
        self.temp_inventory = '{}'

    def set_keyboard(self, k_index, session):
        self.prev_keyboard = self.keyboard
        self.keyboard = k_index
        session.flush()

    # gameEngine type
    def get_item(self, item_id, session, count=1, inventory='temp'):
        if inventory == 'temp':
            inventory = self.temp_inventory_dict()
        else:
            inventory = self.good_inventory_dict()

        if item_id in inventory.keys():
            inventory[item_id] += count
        else:
            inventory[item_id] = count

        if inventory == 'temp':
            self.temp_inventory = str(inventory)
        else:
            self.good_inventory = str(inventory)

        session.flush()

    def remove_item(self, item_id, session, count=1, inventory='temp'):
        if inventory == 'temp':
            inventory = self.temp_inventory_dict()
        else:
            inventory = self.good_inventory_dict()

        if item_id in inventory.keys() and inventory[item_id] >= count:
            if inventory[item_id] == count:
                inventory[item_id] = 0
                del inventory[item_id]
            else:
                inventory[item_id] -= count

            if inventory == 'temp':
                self.temp_inventory = str(inventory)
            else:
                self.good_inventory = str(inventory)

            session.flush()
            return True
        return False

    def get_money(self, amount, session):
        self.money += int(amount)
        session.flush()

    def spend_money(self, amount, session):
        amount = int(amount)

        if self.money >= amount:
            self.money -= amount
            session.flush()
            return True
        else:
            return False
    #

    # marketplace
    def sell(self, item, price, session):
        price_with_com = int(price + price * COMMISSION)
        lots = session.query(LotBuy).filter((LotBuy.item_id == item), (LotBuy.price == price_with_com)).all()

        if not self.remove_item(item, session, inventory='good'):
            return 'У вас нет этого предмета'

        if lots:
            for lot in lots:
                session.delete(lot)
                session.flush()
                if item_transfer(self, lot.owner, item, price, session):
                    server.notification(lot.owner.vk_id, f'Куплен предмет {item} за {price}')
                    return f'Предмет продан. +{price} = {self.money} золота'

        session.add(LotSell(item, self.vk_id, price_with_com))
        session.flush()
        return f'Предмет выставлен на тогровую площадку за {price_with_com} (комиссия {COMMISSION_TEXT})'

    def buy(self, item, price, session, count=1):
        k = 0

        lots = session.query(LotSell).filter((LotSell.item_id == item), (LotSell.price == price)).all()
        if lots:
            for lot in lots:
                session.delete(lot)
                session.flush()
                if item_transfer(lot.owner, self, item, price, session):
                    server.notification(lot.owner.vk_id, f'У Вас купили {item} за {price - price * COMMISSION}')
                    k += 1
                if k == count:
                    break

        if k:
            msg = f'Предметы ({k}шт.) куплены. - {price}*{k} = {self.money} золота\n'
        else:
            msg = ''
        if count != k:
            msg += f'Ваши запросы на покупку {item} ({count - k}шт.) выставлены на тогровую площадку'
            session.add_all([LotBuy(item, self.vk_id, price) for _ in range(count - k)])
            session.flush()

        return msg
    #


def item_transfer(sell: User, buy: User, item, price, session):
    if buy.spend_money(price, session):
        sell.get_money(price - price * COMMISSION, session)
        buy.get_item(item, session, inventory='good')
        return True
    return False
