from data.gameEngine.entities.character import ActiveCharacter


class Attack:
    name = '?AttackName?'
    self_pos = []  # Список позиций с которых можно использовать эту атаку
    target_pos = []  # Список позиций по которым можно бить этой атакой
    damage_multiply = 1  # Множитель урона
    accuracy = 100  # Шанс попадания в процентах. Может быть больше 100
    stamina_consume = 0  # Затраты выносливости на использование

    @classmethod
    def may_choose(cls, actor_pos):
        return actor_pos in cls.self_pos

    @classmethod
    def may_do(cls, target_pos):
        return target_pos in cls.target_pos

    @classmethod
    def hit_chance(cls, actor: ActiveCharacter, target: ActiveCharacter):
        return cls.accuracy + actor.s_lck_add - target.dodge_chance()


class DirtyStab(Attack):
    name = 'Подлый тычёк'
    self_pos = [1, ]
    target_pos = [1, 2]
    damage_multiply = 1
    accuracy = 100
    stamina_consume = 8


ATTACKS = {
    'DiS': DirtyStab,
}
