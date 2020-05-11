from data.gameEngine.entities.character import PassiveCharacter

ENEMIES = [None, ]


class e_SkeletonWeak(PassiveCharacter):
    name = 'Древний скелет'
    lvl = 7

    s_str_base = 4
    s_dex_base = 1
    s_lck_base = 2


ENEMIES.append(e_SkeletonWeak)
