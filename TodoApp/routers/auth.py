#APIRouter 可以被看作是一个“迷你版的 FastAPI 应用”。
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from models import Users
from sqlalchemy.orm import Session 
from passlib.context import CryptContext
from database import SessionLocal, engine
router = APIRouter()

def  get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    

# 1. 创建 CryptContext 实例
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# 2. 创建一个密码哈希的辅助函数
def get_password_hash(password: str) -> str:
    """对密码进行哈希处理"""
    return bcrypt_context.hash(password)

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str   # 注意：这里接收的是明文密码
    role: str
    is_active: bool = True 

db_dependency =  Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    
    existing_user = db.query(Users).filter(
        (Users.username == create_user_request.username) | 
        (Users.email == create_user_request.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or Email already exists."
        )
    user_data = create_user_request.model_dump(exclude={"password"})
    
    create_user_model = Users(
        **user_data,   # 字典解包”（Dictionary Unpacking),将键值对转为关键字参数
        hashed_password=get_password_hash(create_user_request.password)
    )
    
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return create_user_model
    # print(f'message: User created successfully, username: {create_user_model.username}')
    # return create_user_model

@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    return 'token'