class EnemyType:
    id = 0
    name = '?EnemyName?'
    lvl = 0

    s_rea_base = 0
    s_stm_base = 0
    s_agl_base = 0
    s_int_base = 0
    s_att_base = 0
    s_str_base = 0
    s_dex_base = 0
    s_lck_base = 0

    weapon = ''

    @classmethod
    def make_turn(cls, user, session):
        pass


class e_SkeletonWeak(EnemyType):
    id = 1
    name = 'Древний скелет'
    lvl = 7

    s_str_base = 4
    s_dex_base = 1
    s_lck_base = 2
    s_agl_base = -3

    weapon = 'w_rus'

    @classmethod
    def make_turn(cls, user,  session):
        return user


# -------------~
# ENEMY GROUP
# -------------~


ENEMY_GROUPS = {}


class ge_EnemyGroup:
    level = 0
    enemies = []


class ge_FirstEncounter(ge_EnemyGroup):
    level = 7
    enemies = [1, None, None]


ENEMY_GROUPS[1] = ge_FirstEncounter
