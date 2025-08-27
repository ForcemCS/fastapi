#APIRouter 可以被看作是一个“迷你版的 FastAPI 应用”。
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, Field
from models import Users
from sqlalchemy.orm import Session 
from passlib.context import CryptContext
from database import SessionLocal, engine
import jwt
from jwt.exceptions import InvalidTokenError

router = APIRouter()

# 这是一个极其重要的密钥！ JWT 的安全性依赖于此。当你创建一个 JWT 时，你会用这个密钥对其进行数字签名。当服务器收到一个 JWT 时，它会用同一个密钥来验证签名是否有效。如果签名无效，说明令牌要么被篡改过，要么根本就不是你签发的。在生产环境中，这个密钥必须是复杂、随机且保密的，绝不能硬编码在代码里。
SECRET_KEY = "1924e09809ce697b20613a89a3875b1a0658dc488b6b4128e0ef4539b109e1a4"
ALGORITHM = "HS256"

# 去/token这个接口获取url
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

class Token(BaseModel):
    access_token: str
    token_type: str

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

def authenticate_user(username: str, password: str,  db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    # 创建载荷（Payload）的核心数据, id: 用来存放用户的数据库 ID。 role: 用来存放用户的角色（如 admin, user），这对于做权限控制非常有用。
    encode = {'sub': username, 'id': user_id, 'role': role}
    # 计算令牌的过期时间
    expires = datetime.now(timezone.utc) + expires_delta
    # 将过期时间添加到载荷中
    encode.update({'exp': expires})
    # 编码生成最终的 JWT 令牌
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# 检查门票：如果一个请求来了，并且是访问受保护的资源（比如一个需要登录的接口），服务器的“保安” (get_current_user 函数) 就会说：“请出示你的门票（Token）！”
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
        return {"username": username, "id": user_id, "user_role": user_role}
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")


@router.post("/user", status_code=status.HTTP_201_CREATED)
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

# 我想为某个用户获取access_token,先检查这个用户存不存在
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}

