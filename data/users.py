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
    tech_id = sqlalchemy.Column(sqlalchemy.String)
    count_view = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    count_random = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    go_ahead = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    def __init__(self, discord_id, tech_id):
        self.discord_id = discord_id
        self.tech_id = tech_id

    def __repr__(self):
        return f"Рейтинг: {self.rating}\n\
Кол-во игр за предателя: {self.count_impostor} \nКол-во игр\
за члена экипажа: {self.count_crew},\nКол-во выиграных игр за предателя\
: {self.impostor_win}\nКол-во выиграных игр за члена экипажа: {self.crew_win}"
