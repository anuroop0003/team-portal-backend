from sqlalchemy.orm import Session
from app.models.user_model import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------- Helpers --------
def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


# -------- Create User --------
def create_user(db:Session, user_data):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if(existing):
        raise Exception("User already exists")
    
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        role=user_data.role,
        hashed_password=hash_password(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# -------- Get All Users --------
def get_users(db:Session):
    return db.query(User).all()

# -------- Get User By ID --------
def get_user_by_id(db:Session, user_id:int):
    return db.query(User).filter(User.id== user_id).first()

# -------- User Soft Delete --------
def deactivate_user(db:Session, user_id:int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise Exception("User not found")

    user.is_active = False
    db.commit()
    return user
