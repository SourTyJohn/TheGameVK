import vk_api
from data.tokens import *
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from data import db_session
db_session.global_init("db/global.db")

from data.db_models._users import User, LotBuy, LotSell
from data.db_models._items import show_inventory, show_item, init_items, ITEMS
import random as rd

ITEMS_PER_PAGE = 10


vk_session = vk_api.VkApi(token=BOT_TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)


# == USER ==
def getOwnUser(vk_id, session) -> User:
    player = session.query(User).get(vk_id)
    return player


def checkKeyboard(user):
    return user.keyboard
# == ==


# == DUNGEON ==
def f_prepare(user, session, text):
    user.set_keyboard(3, session)
    return "Вы отправляетесь в подземелье. " \
           "Выберите сначала позицию в отряде, а затем какого персонажа туда назначить"
# == ==


# == ИНВЕНТАРЬ ==
def f_inventory_main(user, session, text):
    user.set_keyboard(4, session)
    inv, inv_len = show_inventory(user.good_inventory_dict(), session)
    return f'ИНВЕНТАРЬ  /  Золота: {user.money}\n\n{inv}'


def f_inventory_help(*args):
    return 'о <номер или id предмета> (Осмотреть)\n\n' \
           'п <номер или id предмета> <цена>\n\n' \
           'к <номер или id предмета> <цена> [опционально: кол-во запросов]'


def f_show_item_good(user, session, text):
    try:
        return show_item(get_id_from(text, user, session), session, full=True)

    except Exception:
        return 'что-то пошло не так'
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
                sells[x.item_id] = max(ses, key=lambda x: x.price).price
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
    return 'п (продать) <id предмета> <цена>\n\n' \
           '"к (купить) <id предмета> <цена> [кол-во]" или "к <номер слота на т.площадке>"\n\n' \
           'с (сортировать по цене) <1, 0, -1> (1 возрастание, -1 убывание, 0 не сортировать)\n\n' \
           'н (найти) <id предмета>'


def f_my_lots_help(*args):
    return 'у (удалить) <id лота (первое число в строке лота)>'
# == ==


def view_hero(number):
    pass


def select_hero(number):
    pass


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
    session.add(user)
    session.flush()

    user.get_item('tab', session, 5, inventory='good')
    user.get_item('pob', session, 1, inventory='good')
    return 'Вы успешно зарегестрировались'


def f_goto_menu(user, session, *args):
    user.set_keyboard(2, session)
    return 'Главное меню'
# == ==
