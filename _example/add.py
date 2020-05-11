from flask import Flask
from data import db_session
from data.users import User
from data.jobs import Job


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/blog.db")
    session = db_session.create_session()

    news = list()
    news.append(User(surname='Scott', name='Ridley', age='21', position='captain',
                     speciality='research engineer', address='module_1', email='scott_chief@mars.org)'))
    news.append(Job(team_leader=1, job='работа-1'))

    for x in news:
        session.add(x)
    session.commit()


if __name__ == '__main__':
    main()
