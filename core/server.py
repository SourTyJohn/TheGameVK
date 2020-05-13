import vk_api
from data.tokens import *
from vk_api.bot_longpoll import VkBotLongPoll

from data import db_session
from data.db_models._users import User, LotBuy, LotSell, MAX_HEROES
from data.db_models._passiveHeroes import PassiveHero, STATS_NAMES, STATS
from data.gameEngine.entities.character import RND_NAMES
from data.db_models._items import *
import random as rd

db_session.global_init("db/global.db")

vk_session = vk_api.VkApi(token=BOT_TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

ITEMS_PER_PAGE = 10

HELP_INVENTORY = 'о (Осмотреть) <номер или id предмета>\n\n' \
           'п (Продать) <номер или id предмета> <цена>\n\n' \
           'к (Купить) <номер или id предмета> <цена> [опционально: кол-во запросов]\n\n' \
           'и (Использовать) <номер или id предмета>'

CHARACTER_HELP = '''Сила : +++Урон в тяжёлым оружием
Ловкость: +Увороты  +Урон лёгким оружием  ++Урон из луков
Реакция: +++Увороты. Определяет очерёдность ходов
Выносливость: +++Выносливость
Телосложение: +++Здоровье
Интеллект: ++Эффективность заклинаний
Удача: ++Качество найденных предметов  +Шанс крит.урона
Внимательность: +++Шанс найти предмет'''
# ----
# у (Улучшить) <id параметра>'''
# выгнать (Выгнать) <номер героя> Вы навсегда потеряете этого персонажа'''

MARKET_HELP = 'п (Продать) <id предмета> <цена>\n\n' \
              'к (Купить) <id предмета> <цена> [кол-во] ' \
              'к (Купить) <номер слота на т.площадке>\n\n' \
              'н (Найти) <id предмета>'

MY_LOTS_HELP = 'у (Удалить) <id лота (первое число в строке лота)>'


# == USER ==
def getOwnUser(vk_id, session) -> User:
    player = session.query(User).get(vk_id)
    return player


def checkKeyboard(user):
    return user.keyboard
# == ==


# == DUNGEON ==
def f_prepare(user: User, session, text):
    user.set_keyboard(3, session)

    # TEST
    for i, hero in enumerate(user.get_heroes_list()):
        user.activate_hero(hero, i + 1, session)
    #

    return "Вы отправляетесь в подземелье.\n" \
           'Выберите позицию в отряде. Оружие стоит подбирать в зависимости от позиции\n' \
           'Текущий отряд\n' \
            f'1{user.h1}\n' \
            f'2{user.h2}\n' \
            f'3{user.h3}\n'


def f_chose_pos(user, session, text):
    return 'Временно не доступно'

    if len(text) > 1 and text[1].isdigit() and 0 < int(text[1]) < 4:
        user.selected_slot = int(text[1])

        characters = user.get_heroes_list()

        ch_str = ''
        for i, x in enumerate(characters):
            ch_str += f'{i + 1} {str(x)}'

        user.set_keyboard(11, session)
        return 'Выберите персонажа на эту позицию:\n\n' + ch_str
    return 'Неверная команда'


def f_weapon_select_menu(user, session, text):
    pass


def f_item_select_menu(user, session, text):
    pass


def f_show_weapons(user, session, text):
    inv = ''

    for x in user.good_inventory_dict().keys():
        if str(ITEMS[x].__name__)[0] == 'w':
            inv += show_item(x, session)

    return inv


def f_chose_weapon(*args):
    try:
        pass

    except Exception:
        return 'что-то не так'


def f_dungeon_character(user, session, text):
    user.selected_slot_2 = user.selected_slot
    get_id_character(user, text)
    user.set_keyboard(12, session)
    return 'Выберите оружие для этого персонажа'


def f_goto_dungeon(*args):
    pass

# == ==


# == CHARACTERS ==
def f_characters_main(user, session, text):
    user.set_keyboard(8, session)
    characters = user.get_heroes_list()

    ch_str = ''
    for i, x in enumerate(characters):
        ch_str += f'{i + 1} {str(x)}'

    return f'ПЕРСОНАЖИ {len(user.get_heroes_list())} / {MAX_HEROES}\n\n' + ch_str


def f_character(user, session, text):
    hero = get_id_character(user, text)
    if hero is not None:
        user.set_keyboard(9, session)
        return hero.show()
    else:
        return 'У Вас нет такого персонажа'


def f_character_delete(user, session, text):
    return user.del_hero(session)


def get_id_character(user, text):
    if len(text) > 1 and text[1].isdigit() and 1 <= int(text[1]) <= MAX_HEROES:
        heroes = user.get_heroes_list()
        k = int(text[1])
        if k < len(heroes) + 1:
            user.selected_slot = k - 1
            return heroes[k - 1]


def f_character_help(*args):
    return CHARACTER_HELP


def f_character_upgrade_main(user, session, text):
    user.set_keyboard(10, session)
    return 'Выберите параметр по его id.' \
           'Про параметры Вы можете прочитать нажав Назад, потом Справка'


def f_character_upgrade(user, session, text):
    if len(text) > 1 and text[1] in ['str', 'dex', 'rea', 'stm', 'agl', 'int', 'lck', 'att']:
        hero: PassiveHero = user.get_heroes_list()[user.selected_slot]
        if hero.s_free == 0:
            return 'Не хватает очков параметров'
        stats = hero.open_stats()
        stat = text[1]
        stats[stat] += 1
        stats['free'] -= 1
        hero.close_stats(stats)
        return f'+ 1 {STATS_NAMES[stat]} = {stats[stat]}'
    return 'Неверная команда'


# == ИНВЕНТАРЬ ==
def f_inventory_main(user, session, text):
    user.set_keyboard(4, session)
    inv, inv_len = show_inventory(user.good_inventory_dict(), session)
    return f'ИНВЕНТАРЬ  /  Золота: {user.money}\n\n{inv}'


def f_inventory_help(*args):
    return HELP_INVENTORY


def f_show_item_good(user, session, text):
    try:
        iid, tp = get_id_from(text, user, session)
        return show_item(iid, session)

    except Exception:
        return 'что-то пошло не так'


def f_use_from_inv(user, session, text):

    try:
        iid, tp = get_id_from(text, user, session)
        code = ITEMS[iid].use(user, session)

        if not code:
            return 'У Вас нету этого предмета'

        if code == 'openB#1':
            return getRngItem(user, session, LT_BOX, 10)
        else:
            return code

    except Exception:
        return 'Что-то не так'


# == ==


# == ТОРГОВАЯ ПЛОЩАДКА ==
def f_sell(user, session, text):
    try:
        if len(text) == 3:
            iid, tp = get_id_from(text, user, session)
            return user.sell(iid, int(text[2]), session)
        else:
            return 'Что-то не так. Нажмите Помощь'

    except ValueError:
        return 'Что-то не так. Нажмите Помощь'


def f_buy(user, session, text):
    try:
        iid, tp = get_id_from(text, user, session)
        if tp:
            return user.buy(iid.item_id, iid.price, session)

        elif len(text) == 4:
            return user.buy(iid, int(text[2]), session, int(text[3]))

        elif len(text) == 3:
            return user.buy(iid, int(text[2]), session)

        else:
            return 'Что-то не так. Нажмите Помощь'

    except ValueError:
        return 'Что-то не так. Нажмите Помощь'


def f_delete_lot(user, session, text):
    if len(text) > 1 and text[1].isdigit():
        lot_id = text[1]
        try:
            if lot_id[0] == '1':
                lot = session.query(LotSell).get(int(lot_id[1:]))
                user.get_item(lot.item_id, session)
                session.delete(lot)
                session.flush()
                return 'Лот удалён. Предмет возвращён в инвентарь'

            elif lot_id[0] == '2':
                session.delete(session.query(LotBuy).get(int(lot_id[1:])))
                session.flush()
                return 'Запрос на покупку удалён'

        except Exception:
            return 'Что-то не так. Нажмите Помощь'
    return 'Что-то не так. Нажмите Помощь'


# page
def f_first_page(user: User, *args):
    user.page = 0
    return 'Страница: 1'


def f_prev_page(user, session, text):
    if user.page > 0:
        user.page -= 1

    if user.keyboard == 5:
        return f_marketplace(user, session, text)
    elif user.keyboard == 6:
        return f_show_my_lots(user, session, text)


def f_next_page(user, session, text):
    user.page += 1

    if user.keyboard == 5:
        return f_marketplace(user, session, text)
    elif user.keyboard == 6:
        return f_show_my_lots(user, session, text)
#


def f_marketplace(user, session, text=None):
    page = get_page(user, text)
    user.set_keyboard(5, session)

    trd, c_lots_sell, c_lots_buy = get_trades(session, user, page)

    return f'Торговая площадка. Лотов: {c_lots_sell}  ' \
           f'Запросов на покупку: {c_lots_buy}\nСтраница: {user.page + 1}\n\n{get_trades_txt(trd, session)}'


def f_find_in_market(user, session, text):
    user.set_keyboard(7)
    user.search = text[1]
    return f_marketplace(user, session, ['н', 1])


def f_search_clear(user, session, text):
    user.search = None
    return f_marketplace(user, session, text)


def f_show_my_lots(user, session, text):
    page = get_page(user, text)
    user.set_keyboard(6, session)
    trd = get_trades_my(user, session, page)
    return f'Мои лоты. Страница: {user.page + 1}\n\n' + trd


def get_page(user, text):
    if len(text) > 1 and type(text[1]) == int:
        page = int(text[1]) - 1
    else:
        page = user.page
    return page


# get trades
def get_trades_txt(trades, session):
    txt_trd = ''
    sells = {}

    for x in trades:
        txt_trd += str(x)
        if x.item_id not in sells.keys():
            ses = session.query(LotBuy).filter(LotBuy.item_id == x.item_id).all()
            if ses:
                sells[x.item_id] = max(ses, key=lambda y: y.price).price
            else:
                sells[x.item_id] = 'нет'

        txt_trd += f'Текущая максимальная стоимость покупки: {sells[x.item_id]}\n\n'
    return txt_trd


def get_trades(session, user, page):
    if user.search:
        trd = session.query(LotSell).filter(LotSell.item_id.like(user.search))
        buy = session.query(LotBuy).filter(LotBuy.item_id.like(user.search)).count()

    else:
        trd = session.query(LotSell)
        buy = session.query(LotBuy).count()

    if not trd:
        return 'Пустая страница', 0, 0

    else:
        count_sell = trd.count()
        trd = trd.filter((page * ITEMS_PER_PAGE <= LotSell.id), (LotSell.id <= (page + 1) * ITEMS_PER_PAGE))
        return trd, count_sell, buy

    # if sorts:
    #     trd = sorted(trd, key=lambda lot: lot.price * sorts)


def get_trades_my(user, session, page):
    txt_trd = ''

    for x in session.query(LotSell).filter((page * ITEMS_PER_PAGE <= LotSell.id), (LotSell.owner_id == user.vk_id)):
        txt_trd += '1' + str(x)

    for x in session.query(LotBuy).filter((page * ITEMS_PER_PAGE <= LotBuy.id), (LotBuy.owner_id == user.vk_id)):
        txt_trd += '2' + str(x)

    return txt_trd
#


def f_market_help(*args):
    return MARKET_HELP


def f_my_lots_help(*args):
    return MY_LOTS_HELP
# == ==


# == ОБЩЕЕ ==
def get_id_from(text, user, session):
    if not text[1].isdigit():
        item_id, id_type = text[1], False

    elif user.keyboard == 4:
        item_id, id_type = list(user.good_inventory_dict().keys())[int(text[1]) - 1], False

    else:
        item_id, id_type = session.query(LotSell).get(int(text[1])), True

    return item_id, id_type


# Quick message without keyboard
def notification(user, message):
    vk.messages.send(user_id=user, message=message, random_id=rd.randint(0, 2 ** 32))


def f_back(user, session, text):
    user.keyboard = user.prev_keyboard
    session.flush()
    if user.keyboard == 4:
        return f_inventory_main(user, session, text)
    return '...'


def f_start(vk_id, session, *args):
    user = User(vk_id)

    names = rd.choices(RND_NAMES, k=3)
    p1 = PassiveHero(names[0], user.vk_id)
    p2 = PassiveHero(names[1], user.vk_id)
    p3 = PassiveHero(names[2], user.vk_id)

    session.add_all([user, p1, p2, p3])
    session.flush()

    user.new_hero(session, p1.id)
    user.new_hero(session, p2.id)
    user.new_hero(session, p3.id)
    user.get_item('lub', session, 1)

    print(f'New Player Added. ID: {user.vk_id}')
    return 'Вы успешно зарегестрировались. В инвентаре стартовый подарок\n' \
           'Загляните так же в меню персонажей и распределите очки опыта'


def f_goto_menu(user, session, *args):
    if user.h1:
        user.h1.exit(session)
    if user.h2:
        user.h2.exit(session)
    if user.h3:
        user.h3.exit(session)

    user.set_keyboard(2, session)
    return 'Главное меню'
# == ==
