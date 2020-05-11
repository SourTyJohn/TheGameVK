from flask import Flask
from data import db_session
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/blogs.sqlite")
    add_some_men()


def add_some_men():
    session = db_session.create_session()

    news = list()
    news.append(User(surname='Scott', name='Ridley', age='21', position='captain',
                speciality='research engineer', address='module_1', email='scott_chief@mars.org)'))
    news.append(User(surname='John', name='Sour', age='22', position='non-captain',
                     speciality='research engineer', address='module_1', email='sco1tt_chief@mars.org)'))
    news.append(User(surname='Wolfgang', name='Duff', age='23', position='non-captain',
                     speciality='research engineer', address='module_2', email='scot2t_chief@mars.org)'))
    news.append(User(surname='Gunn', name='Heuze', age='18', position='captain',
                     speciality='research engineer', address='module_5', email='lady@mars.org)'))

    for x in news:
        session.add(x)
    session.commit()


if __name__ == '__main__':
    main()
