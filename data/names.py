import sqlalchemy

from .db_session import SqlAlchemyBase


class Names(SqlAlchemyBase):
    __tablename__ = "Names"
    name = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    owner_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))

    def __init__(self, name, owner_id):
        self.name = name
        self.owner_id = owner_id