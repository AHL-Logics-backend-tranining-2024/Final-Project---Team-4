from uuid import UUID
from sqlmodel import Session, select
from app.models import User
from app.settings import Settings
from app.utils.security import verify_password


settings = Settings.get_instance()

class AuthService:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_username(self, username: str) -> User | None:
        user = self.session.exec(select(User).where(User.username == username)).first()
        if user:
            return user
        return None
    
    def get_user_by_id(self, id: UUID) -> User | None:
        user = self.session.exec(select(User).where(User.ID == id)).first()
        if user :
            return user
        return None
    

    async def authenticate_user(self, username: str, password: str) -> User | None:
        user = self.get_user_by_username(username)
        if user and verify_password(password, user.hashed_password):
            return user
        return None
     