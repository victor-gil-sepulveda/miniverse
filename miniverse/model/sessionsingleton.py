from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from miniverse.model.model import Base


class _Singleton(type):
    """ A metaclass that creates a Singleton base class when called. """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(_Singleton('SingletonMeta', (object,), {})):
    pass


class DbSessionHolder(Singleton):
    """
    Keeps a copy of the session maker of sqlalchemy to be used when needed.
    """
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.Session = None
        self.reset()

    def reset(self):
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()
