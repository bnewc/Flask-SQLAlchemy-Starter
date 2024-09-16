"""Config for application"""
from os import getenv
from os.path import join, dirname, abspath
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# -------------Environment settings----------------------------------
ENV = getenv("FLASK_ENV", default="production")
DEBUG = ENV == "development"
SQLALCHEMY_ECHO = getenv("ECHO") == "True"
SECRET_KEY = getenv("SECRET_KEY")


# -------------SQLAlchemy Settings-----------------------------------
def get_local_db():
    """Returns path of local SQLite testing database"""
    project_dir = dirname(abspath(__file__))
    return "sqlite:///{}".format(join(project_dir, "testdb.db"))


SQLALCHEMY_DATABASE_URI = getenv(
    "SQLALCHEMY_DATABASE_URI", default=get_local_db()
)
SQLALCHEMY_TRACK_MODIFICATION = getenv(
    "SQLALCHEMY_TRACK_MODIFICATIONS", default=False
)


if __name__ == '__main__':
    pass
