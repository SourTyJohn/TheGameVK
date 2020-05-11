from data.gameEngine.contents.weapons import *


class Item:
    id = 0
    name: str = "ItemName"
    description: str = 'ItemDescription'

    eatable: bool = False  # Можно ли съесть этот предмет
    throwable: bool = False  # Можно ли кинуть этот предмет
    item_type = 1
    rarity = 1

    @classmethod
    def eat(cls, actor: ActiveCharacter):
        pass

    @classmethod
    def throw(cls, actor: ActiveCharacter, target: ActiveCharacter):
        pass

    @classmethod
    def set(cls):
        return cls.name, cls.rarity, cls.item_type, cls.id


class i_Bread(Item):
    id = 'tab'
    name = 'Вкусный хлеб'
    description = ['"Нежный мякишь и хрустящая корочка составляют вкуснейший дуэт"',
                   '- Л. Густатус, авторитетный гурман из Лангарда']

    eatable = True
    regenerate_amount = 4
    throwable = False

    @classmethod
    def eat(cls, actor):  # actor - _activeHero, _activeEnemy
        actor.health_regenerate(cls.regenerate_amount)


class i_PoisonBottle(Item):
    id = 'pob'
    name = 'Склянка с Ядом'
    description = ['Можно бросить в противника, чтобы отравить его',
                   'Пить не рекомендуется']
    eatable = True
    throwable = True

    @classmethod
    def eat(cls, actor):
        actor.health_damage(4)

    @classmethod
    def throw(cls, actor: ActiveCharacter, target: ActiveCharacter):
        pass
