from data.gameEngine.entities.character import ActiveCharacter
from data.gameEngine.contents.attacks import Attack, ATTACKS


# WEAPON TAGS


def sharpness(hero, attack, enemy_team, target_pos):
    pass


WEAPON_TAGS = [
    {'effect': sharpness, 'rarity': 1, 'name': 'Острый', 'description': '+урон'},
]


# WEAPON TAGS


class Weapon:
    item_type = 4
    w_id = '?WeaponID?'

    name = "?WeaponName?"
    description = ['?WeaponDescription?', ]

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
    w_id = 'Dag'
    name = 'Кинжал'
    attacks = [ATTACKS['DiS'], ]
    param_scaling = {'dex': 0.3, 'rea': 0.1}
    perks_scaling = {}


class w_GreatSword(Weapon):
    w_id = 'GrS'
    name = 'Двуручный меч'
    attacks = []
    param_scaling = {'dex': 0.1, 'str': 1}
    perks_scaling = {}
