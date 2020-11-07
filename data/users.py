import sqlalchemy

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = "users"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    names = sqlalchemy.Column(sqlalchemy.String)
    rating = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    count_impostor = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    count_crew = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    impostor_win = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    crew_win = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    discord_id = sqlalchemy.Column(sqlalchemy.Integer)