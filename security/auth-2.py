from datetime import datetime, timedelta, timezone
from typing import Annotated, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import SessionLocal
from models import Users
import jwt
from jwt.exceptions import InvalidTokenError

# ==========================
# 配置和初始化
# ==========================
router = APIRouter(prefix='/auth', tags=['auth'])

SECRET_KEY = "your-secret-key"   # ✅ 生产环境请用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 20
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ 黑名单（简单用内存存储，可以换成 Redis）
TOKEN_BLACKLIST = set()

# ==========================
# Pydantic 模型
# ==========================
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    is_active: bool = True

# ==========================
# 数据库依赖
# ==========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# ==========================
# 密码处理
# ==========================
def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)

def authenticate_user(username: str, password: str, db) -> Users | bool:
    user = db.query(Users).filter(Users.username == username).first()
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

# ==========================
# JWT 创建与解析
# ==========================
def create_token(data: Dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    payload.update({"exp": datetime.now(timezone.utc) + expires_delta})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")

# ==========================
# 获取当前用户
# ==========================
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_token(token)
    return {
        "username": payload.get("sub"),
        "id": payload.get("id"),
        "role": payload.get("role")
    }

# ==========================
# API 路由
# ==========================

# 1. 注册新用户
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    existing_user = db.query(Users).filter(
        (Users.username == create_user_request.username) |
        (Users.email == create_user_request.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or Email already exists.")
    
    user_data = create_user_request.model_dump(exclude={"password"})
    create_user_model = Users(**user_data, hashed_password=get_password_hash(create_user_request.password))
    
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return create_user_model

# 2. 登录，返回 Access 和 Refresh Token
@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")
    
    access_token = create_token(
        {"sub": user.username, "id": user.id, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_token(
        {"sub": user.username, "id": user.id, "role": user.role, "type": "refresh"},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

# 3. 刷新 Access Token
@router.post("/refresh")
async def refresh_access_token(request: RefreshRequest):
    if request.refresh_token in TOKEN_BLACKLIST:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked.")
    
    payload = decode_token(request.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")
    
    new_access_token = create_token(
        {"sub": payload["sub"], "id": payload["id"], "role": payload["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": new_access_token, "token_type": "bearer"}

# 4. 注销（撤销 Refresh Token）
@router.post("/logout")
async def logout(request: LogoutRequest):
    TOKEN_BLACKLIST.add(request.refresh_token)
    return {"message": "Logged out successfully."}