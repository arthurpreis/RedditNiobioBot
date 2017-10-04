from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, User, Comment
from sqlalchemy.exc import IntegrityError


# Prepara e executa algumas funções no db
class Database:
    def __init__(self, driver, username, password, host, port, database):
        self.driver = driver
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database

        # Configura o db assim que o objeto for instanciado
        self._connect()
        self._create_tables()
        self._make_session()

    def _connect(self):
        url = ('{driver}://{username}:{password}@'
               '{host}:{port}/{database}?charset=utf8')
        engine = create_engine(url.format(**self.__dict__),
                               encoding='utf-8',
                               pool_recycle=1)
        self.engine = engine

    # Cria as tabelas no db caso não existam
    def _create_tables(self):
        Base.metadata.create_all(self.engine)

    def _make_session(self):
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def get_or_add_user(self, **kwargs):
        query = self.session.query(User).filter_by(**kwargs).first()
        if query is not None:
            return query
        else:
            try:
                user = User(**kwargs)
                self.session.add(user)
                self.session.commit()
                return user
            except IntegrityError:
                self.session.rollback()

    def add_comment(self, **kwargs):
        comment = Comment(**kwargs)
        self.session.add(comment)
        self.session.commit()
        return comment

    def get_comment(self, **kwargs):
        query = self.session.query(Comment).filter_by(**kwargs).first()
        return query

    def get_comments(self, **kwargs):
        query = self.session.query(Comment).filter_by(**kwargs).all()
        return query
