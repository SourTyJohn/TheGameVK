import vk_api
import vk_api.keyboard
from core import server as sv

B_COLORS = [
    vk_api.keyboard.VkKeyboardColor.DEFAULT,
    vk_api.keyboard.VkKeyboardColor.PRIMARY,
    vk_api.keyboard.VkKeyboardColor.POSITIVE,
    vk_api.keyboard.VkKeyboardColor.NEGATIVE
]

BUTTON_MENU = ['Меню', 2, 1]
BUTTON_HELP = ['Помощь', 0, 1]
BUTTON_BACK = ['Назад', 2, 1]


def create_keyboard(buttons: list, one_time=False, inline=False):
    # Buttons = [[text, color, new_line], [...], ]
    keyboard = vk_api.keyboard.VkKeyboard(one_time=one_time, inline=inline)

    for i, button in enumerate(buttons):
        if button[2]:
            keyboard.add_line()
        keyboard.add_button(button[0], color=B_COLORS[button[1]])

    return keyboard.get_keyboard()


class Keyboard:
    board = create_keyboard([])
    commands = {}
    text = '?KeyboardText?'
    back_command = None

    @classmethod
    def get_board(cls, *args):
        return cls.board


class k_MainMenu(Keyboard):
    """Главное меню"""
    board = create_keyboard([['Подземелье', 1, False],
                             ['Инвентарь', 0, True], ['Персонажи', 0, False],
                             ['Торговая_площадка', 1, True],
                             ['Арена', 3, True]])
    commands = {'подземелье': sv.f_prepare, 'инвентарь': sv.f_inventory_main,
                'торговая_площадка': sv.f_marketplace}


class k_YesNoClose(Keyboard):
    board = create_keyboard([['Да', 2, False], ['Нет', 3, False],
                             ['Закрыть', 0, True]])
    commands = {}

    @classmethod
    def is_command_exists(cls, command):
        return command in cls.commands.keys()


class K_PreDungeon(Keyboard):
    """Меню выбора героев для похода"""
    board = create_keyboard([['1', 1, 0], ['2', 1, 0], ['3', 1, 0]], inline=True)
    commands = {'1': None}


class k_CharacterSelect(Keyboard):
    board = create_keyboard([['1. Осмотреть', 1, 0], ['1. Выбрать', 1, 0],
                             ['2. Осмотреть', 1, 1], ['2. Выбрать', 1, 0],
                             ['3. Осмотреть', 1, 1], ['3. Выбрать', 1, 0],
                             ['4. Осмотреть', 1, 1], ['4. Выбрать', 1, 0],
                             ['5. Осмотреть', 1, 1], ['5. Выбрать', 1, 0]])
    commands = {}
    for x in range(1, 6):
        pass


class k_Inventory(Keyboard):
    board = create_keyboard([['Обновить', 1, 0],
                             BUTTON_HELP,
                             BUTTON_MENU])
    commands = {'обновить': sv.f_inventory_main, 'меню': sv.f_goto_menu,
                'о': sv.f_show_item_good, 'o': sv.f_show_item_good,
                'п': sv.f_sell, 'к': sv.f_buy,
                'помощь': sv.f_inventory_help}


class k_Marketplace(Keyboard):
    board = create_keyboard([['<--', 1, 0], ['Обновить', 1, 0], ['-->', 1, 0],
                             ['Мои_лоты', 1, 1],
                             BUTTON_HELP,
                             BUTTON_MENU])

    commands = {'обновить': sv.f_marketplace, 'меню': sv.f_goto_menu,
                '<--': sv.f_prev_page, '-->': sv.f_next_page,
                'п': sv.f_sell, 'к': sv.f_buy,
                'помощь': sv.f_market_help,
                'н': sv.f_find_in_market, 'мои_лоты': sv.f_show_my_lots}


class k_MarketplaceSearch(k_Marketplace):
    board = create_keyboard([['<--', 1, 0], ['Обновить', 1, 0], ['-->', 1, 0],
                             ['Отменить_поиск', 1, 1],
                             BUTTON_HELP,
                             BUTTON_MENU])

    commands = k_Marketplace.commands.copy()
    del commands['мои_лоты']
    commands['отменить_поиск'] = sv


class k_MyLots(Keyboard):
    board = create_keyboard([['Обновить', 1, 0],
                             BUTTON_HELP,
                             BUTTON_BACK])
    commands = {'назад': sv.f_marketplace, 'помощь': sv.f_my_lots_help, 'у': sv.f_delete_lot,
                'обновить': sv.f_show_my_lots}


KEYBOARDS = {
    2: k_MainMenu,
    3: k_CharacterSelect,
    4: k_Inventory,
    5: k_Marketplace,
    6: k_MyLots,
    7: k_MarketplaceSearch
}
