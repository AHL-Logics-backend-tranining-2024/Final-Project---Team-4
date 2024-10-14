from uuid import UUID
from sqlmodel import Session, select
from app import schemas
from app import models

class UserService:
    def __init__(self, session: Session):
        self.session = session

    def get_users(self , skip : int= 0 , limit : int = 10 , order_by:UUID="id") ->  list[models.User]:
        users = Session.exec(select(models.User).offset(skip).limit(limit).order_by(models.User.id)).all()
        return users

    def create_user(self, user: schemas.CreateUserRequest) -> models.User:
        db_user = models.User(username=user.username, email=user.email, password=user.password)  
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user
    
    def update_user(self, user_id: UUID, user: schemas.UpdateUserRequest) -> models.User:
        db_user = self.session.get(models.User, user_id)
        if db_user:
            db_user.username = user.username
            db_user.email = user.email
            db_user.password = user.password 
            
            self.session.commit()
            self.session.refresh(db_user)
            return db_user
        return None  # User not found

    def delete_user(self, user_id: UUID) -> None:
        db_user = self.session.get(models.User, user_id)
        if db_user:
            self.session.delete(db_user)
            self.session.commit()
            return True
        return False  

