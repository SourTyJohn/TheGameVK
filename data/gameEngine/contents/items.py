from random import randint as ri
from random import random as rd
from data.gameEngine.entities.character import ActiveCharacter
from data.gameEngine.contents.attacks import Attack, ATTACKS


class LootTable:
    loot = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
        6: [],
        7: [],
    }

    def __init__(self):
        self.loot = LootTable.loot.copy()

    def add_loot(self, item):
        self.loot[item.rarity].append(item.id)

    def __getitem__(self, item):
        return self.loot[item]


class Item:
    id = 0
    name: str = "ItemName"
    description: str = ['ItemDescription', ]

    eatable: bool = False  # Можно ли съесть этот предмет
    usable: bool = False  # Можно ли использовать этот предмет вне подземелья
    throwable: bool = False  # Можно ли кинуть этот предмет
    material: bool = False  # Материал для крафта или нет

    item_type = 1
    rarity = 1
    tags = []

    @classmethod
    def throw(cls, actor: ActiveCharacter, target: ActiveCharacter):
        pass

    @classmethod
    def set(cls):
        return cls.name, cls.rarity, cls.item_type, cls.id

    @classmethod
    def use(cls, user, session):
        return 'Вы не можете использовать это сейчас'


#
class Material(Item):
    item_type = 2
    material = True


class i_Clover(Material):
    id = 'clo'
    name = 'Клевер'
    description = ['Четырёхлистный клевер. Пригодится для приготовления зелья удачи', ]

    rarity = 2
    tags = ['Flower', ]


class i_WaterBottle(Material):
    id = 'wab'
    name = 'Бутылка воды'
    description = ['Ну Бутылка воды, что Вам ещё надо?', ]

    rarity = 2


#
class Consumable(Item):
    item_type = 3
    eatable = True

    @classmethod
    def eat(cls, actor: ActiveCharacter):
        return f"{actor.passive.name} потребил {cls.name} и"


class i_Bread(Consumable):
    id = 'tab'
    name = 'Вкусный хлеб'
    description = ['"Нежный мякишь и хрустящая корочка составляют вкуснейший дуэт"',
                   '- Л. Густатус, авторитетный гурман из Лангарда']
    eatable = True

    @classmethod
    def eat(cls, actor):  # actor - _activeHero, _activeEnemy
        actor.health_regenerate(4)


class i_HolyWater(Consumable):
    id = 'how'
    name = 'Святая Вода'
    description = ['Склянка со святой водой. Исцелит любого']

    eatable = True
    throwable = True
    rarity = 6

    @classmethod
    def eat(cls, actor):
        actor.health_regenerate(666)
        return Consumable.eat(actor) + 'восстановил 666 здоровья'

    @classmethod
    def throw(cls, actor: ActiveCharacter, target: ActiveCharacter):
        pass


#
class Usable(Item):
    item_type = 4
    usable = True

    @classmethod
    def use(cls, user, session):
        pass


class i_SmallMoney(Usable):
    id = 'smb'
    name = 'Малый кошелёк'
    rarity = 3
    description = ['"Это ему уже не понадобиться",'
                   'Внутри лежит от 100 до 200 монет']

    @classmethod
    def use(cls, user, session):
        if user.remove_item(cls.id, session):
            if rd() * 100 // 1 < 3:
                amount = 1000
                user.get_money(amount, session)
                return f'Вам крайне повезло и Вы получили {amount} монет.'
            else:
                amount = ri(100, 200)
                user.get_money(amount, session)
                return f'Вы получили {amount} монет.'
        return False


class i_LuckyBox(Usable):
    id = 'lub'
    name: str = "Шкатулка Удачи"
    rarity = 4
    description: str = ['Откройте, чтобы получить случайный предмет или несколько.',
                        'Шанс выпадения будет такой, как если бы у Вас в группе был персонаж с 10 уровнем удачи']

    @classmethod
    def use(cls, user, session):
        if user.remove_item(cls.id, session):
            return 'openB#1'
        return False


# WEAPONS


def sharpness(hero, attack, enemy_team, target_pos):
    pass


WEAPON_TAGS = [
    {'effect': sharpness, 'rarity': 1, 'name': 'Острый', 'description': '+урон'},
]


# WEAPON TAGS


class Weapon(Item):
    item_type = 5
    rarity = 4

    damage = 0
    attacks = []
    param_scaling = {}
    perks_scaling = {}

    @classmethod  # Подсчитывает урон оружия на основе параметров владельца
    def trueDamage(cls, actor: ActiveCharacter, multiply=1):
        damage = cls.damage

        stats = actor.all_stats()
        for s in cls.param_scaling.keys():
            damage += stats[s] * cls.param_scaling[s]

        perks = actor.all_perks()
        for p in cls.perks_scaling.keys():
            if p in perks:
                damage *= cls.perks_scaling[p]

        damage *= multiply
        return damage

    @classmethod
    def full_id(cls):
        return


class w_Dagger(Weapon):
    damage = [3, 7]
    description = ['Небольшой, однако крайне острый клинок', ]
    id = 'dag'
    name = 'Кинжал'
    attacks = [ATTACKS['DiS'], ]
    param_scaling = {'dex': 0.3, 'rea': 0.1}
    perks_scaling = {}


class w_GreatSword(Weapon):
    damage = [8, 14]
    description = ['Из-за длины и веса тяжек в обращении, но бойцы с большой силой смогут с ним управиться', ]
    id = 'grs'
    name = 'Двуручный меч'
    attacks = []
    param_scaling = {'dex': 0.1, 'str': 1}
    perks_scaling = {}


class w_Crossbow(Weapon):
    damage = [10, 12]
    description = ['Арбалет как Арбалет', ]
    id = 'crs'
    name = 'Арбалет'
    attacks = []
    param_scaling = {'dex': 1.2}
    perks_scaling = {}


#  TRINKETS
class Trinket(Item):
    item_type = 6
    rarity = 5


class t_BaseTrinket(Trinket):
    id = 'btr'
    name = 'Амулет'
    description = ['Амулет со случайными магическими свойствами', ]
