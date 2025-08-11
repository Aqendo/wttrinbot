import sqlalchemy.ext.asyncio
import sqlalchemy.orm


class Base(sqlalchemy.ext.asyncio.AsyncAttrs, sqlalchemy.orm.DeclarativeBase):
    pass
