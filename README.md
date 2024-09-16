# Flask-SQLAlchemy Starter

Code I use to start a Flask-SQLAlchemy app. Adapted from [cookiecutter-flask](https://github.com/cookiecutter-flask/cookiecutter-flask).

The most useful additions are found within [`app/database.py`](app/database.py), which features numerous methods to abstract SQLAlchemy operations.

Requires creation of a local `.env` file with Flask-SQLAlchemy [configuration settings](https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/).

Install requirements in a [Python venv](https://docs.python.org/3/library/venv.html) using `pip install -r requirements.txt`.

Read [Flask-SQLAlchemy docs](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/quickstart/) to learn more about usage.