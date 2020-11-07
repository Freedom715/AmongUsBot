import sqlalchemy

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = "users"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    rating = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    count_impostor = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    count_crew = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    impostor_win = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    crew_win = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    failed_game = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    discord_id = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return f"Рейтинг: {self.rating}, кол-во игр за предателя: {self.count_impostor}, кол-во игр\
за члена экипажа: {self.count_crew},\nкол-во выиграных игр за предателя\
: {self.impostor_win}, кол-во выиграных игр за члена экипажа: {self.crew_win}"
