from flask import Flask
from extensions import db


def config_app(config=None):
    if config is None:
        import app.settings as config
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    return app


def main():
    app = config_app()
    with app.app_context():
        pass


if __name__ == '__main__':
    main()
