import requests

from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy


class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///basic_app.sqlite'    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning


def create_app():
    """ Flask application factory """

    # Create Flask app load app.config
    app = Flask(__name__)
    app.config.from_object(__name__ + '.ConfigClass')

    # Initialize Flask-BabelEx

    # Initialize Flask-SQLAlchemy
    db = SQLAlchemy(app)


    def fetch_weather(city):
        url_template = 'http://api.weatherapi.com/v1/current.json?key=&q={}'

        url = url_template.format(city)
        print(url)
        answer = requests.get(url)
        print(answer.json())
        cur = answer.json().get('current')
        temp = cur.get('temp_c')
        return temp

    # Define the User data-model.
    # NB: Make sure to add flask_user UserMixin !!!
    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)

        # User authentication information. The collation='NOCASE' is required
        # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
        username = db.Column(db.String(255), nullable=False, unique=True)
        balance = db.Column(db.Integer)

        @classmethod
        def create(cls, username, balance):
            user = User()
            user.username = username
            user.balance = balance
            db.session.add(user)
            db.session.commit()

        @classmethod
        def update(cls, old, new):
            user = cls.query.filter(cls.username == old['username']).first()
            if not user:
                raise NotImplemented()
            user.username = new['username']
            user.balance = new['balance']
            db.session.commit()

        @classmethod
        def delete(cls, username):
            user = cls.query.filter(cls.username == username).first()
            if not user:
                raise NotImplemented()
            db.session.delete(user)
            db.session.commit()

        @classmethod
        def update_balance(cls, username, new_balance):
            cls.update({'username': username},
                       {'username': username,
                             'balance': new_balance
                        }
                       )

    with app.app_context():
        db.create_all()

        User.create(username='user_0', balance=11000)

        User.create(username='user_1', balance=12000)

        User.create(username='user_2', balance=13000)

        User.create(username='user_3', balance=14000)

        User.create(username='user_4', balance=15000)
        db.session.commit()

    @app.route('/user', methods=['POST'])
    def create_user():
        user = request.form
        User.create(user['username'], user['balance'])
        return 'created'

    @app.route('/user', methods=['DELETE'])
    def delete_user():
        user = request.form
        User.delete(user['username'])
        return 'deleted'

    @app.route('/user', methods=['PUT'])
    def update_user():
        user = request.form
        User.update(user['old'], user['new'])
        return 'updated'

    @app.route('/user', methods=['PATCH'])
    def update_balance():
        user = request.form
        User.update(user['username'], user['balance'])
        return 'updated'

    @app.route('/balance', methods=['PATCH'])
    def update_balance_by_temperature():
        data = request.form
        try:
            balance_delta = fetch_weather(data['city'])
        except Exception:
            return 500, 'error'
        user = User.query.filter(User.id == data['id']).first()
        print(balance_delta, user.balance)
        if 5000 <= user.balance + balance_delta <= 15000:
            user.balance += balance_delta
        db.session.commit()
        return 'updated'

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

