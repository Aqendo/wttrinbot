import sqlalchemy

from wttrinbot.models.base import Base


class Saves(Base):
    __tablename__ = "saves"
    user: int = sqlalchemy.Column(
        sqlalchemy.BigInteger, nullable=False, primary_key=True, index=True
    )
    last_query: str = sqlalchemy.Column(sqlalchemy.String)
