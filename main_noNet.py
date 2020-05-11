from core.keyboards import KEYBOARDS
from core import server

from data.db_session import create_session


def auth_handler():
    key = input("Enter authentication code: ")
    remember_device = True
    return key, remember_device


def event_do(message):
        user_id = 1
        text = message.lower().split()
        session = create_session()
        user = server.getOwnUser(user_id, session)

        if user:
            keyboard = server.checkKeyboard(user)

            if text[0] in KEYBOARDS[keyboard].commands.keys():
                msg = KEYBOARDS[keyboard].commands[text[0]](user, session, text)
                btn = server.checkKeyboard(user)
                send_message(user_id, None, msg, btn)

        else:
            server.start(user_id, session, None)
            send_message(user_id, None, 'Вы зарегестрировались', 2)

        session.commit()


def send_message(user, vk, message, keyboard_type=0):
    print(f'Message send: {message}, keyboard: {KEYBOARDS[keyboard_type].__name__} / {KEYBOARDS[keyboard_type].commands.keys()}')


running = True
while running:
    message = input()
    event_do(message)
