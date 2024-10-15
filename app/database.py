from sqlmodel import Field, Session, SQLModel, create_engine, select
from app.settings import Settings


settings = Settings.get_instance()
engine = create_engine(settings.database_url)

async def init_db():
    try:
       SQLModel.metadata.create_all(engine)
    except Exception:
      raise RuntimeError("Failed to initialize the database.") 



def get_session():
    with Session(engine) as session:
        yield session

async def close_db_connection():
    try:
      engine.dispose()
    except Exception:
        raise RuntimeError("Failed to close the database connection.") 


