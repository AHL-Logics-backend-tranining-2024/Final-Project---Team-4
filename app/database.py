from sqlmodel import Field, Session, SQLModel, create_engine, select
from app.settings import Settings


settings = Settings.get_instance()
engine = create_engine(settings.database_url)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


