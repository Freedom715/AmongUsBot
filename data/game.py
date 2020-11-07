import sqlalchemy

from .db_session import SqlAlchemyBase


class Game(SqlAlchemyBase):
    __tablename__ = "game"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    numb_of_imposters = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    numb_of_crew = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    imposters = sqlalchemy.Column(sqlalchemy.String, default="")
    crew = sqlalchemy.Column(sqlalchemy.String, default="")
    win = sqlalchemy.Column(sqlalchemy.String, default="вылетело")

    def __init__(self, numb_of_imposters, numb_of_crew, imposters, crew):
        self.numb_of_imposters = numb_of_imposters
        self.numb_of_crew = numb_of_crew
        self.imposters = imposters
        self.crew = crew
