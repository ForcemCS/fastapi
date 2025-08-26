# 我们有了一个身份审核员 (authenticate_user)。
# 我们有了一个制卡师 (create_access_token)。
# 我们有了一个VIP区的保安 (get_current_user)。


#Depends: 这是 FastAPI 的依赖注入 (Dependency Injection) 系统核心。它告诉 FastAPI，在执行某个路径操作函数（比如一个 API 接口）之前，需要先执行并获取另一个函数（依赖项）的结果。我们稍后会在 get_current_user 中看到它的威力。
from fastapi import HTTPException, Depends
#这是一个辅助类，专门用来实现 OAuth2 的 "密码授权流程" (Password Flow)。它会告诉 FastAPI：“去请求头里寻找一个 Authorization 字段，并且它的值应该是 Bearer <token> 的形式”。
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext

# 这是一个极其重要的密钥！ JWT 的安全性依赖于此。当你创建一个 JWT 时，你会用这个密钥对其进行数字签名。当服务器收到一个 JWT 时，它会用同一个密钥来验证签名是否有效。如果签名无效，说明令牌要么被篡改过，要么根本就不是你签发的。在生产环境中，这个密钥必须是复杂、随机且保密的，绝不能硬编码在代码里。
SECRET_KEY = "hello-from-escape-team"

# 指定了用于签名的算法。HS256 是一种对称加密算法，意味着加密和解密都使用同一个 SECRET_KEY。
ALGORITHM = "HS256"

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# “如果有人问怎么获取门卡，告诉他们去 /token 这个服务台办理。”
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Mock database of users (replace with your user database logic)
fake_users_db = {
    "user1": {
        "username": "user1",
        "password": "$2b$12$AQyHPwd7p1s.GQvax/A3ve5wMey6NZuDXW1/FVhDpi8s/MV/Fo1LC",  # hashed password: 'password1'
        "disabled": False,
    }
}

# Authentication function
def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not pwd_context.verify(password, user["password"]):
        return False
    return user
# 在门口办会员卡（获取令牌）
# 一旦身份审核通过，他就负责制作一张加密的、防伪的会员卡。
# 它使用 jwt.encode() 这个“加密制卡机”，把这个字典data={"sub": "user1"} 、SECRET_KEY（密钥，相当于制卡的防伪墨水）和 ALGORITHM（算法，相当于制卡的模板）一起放进去。
# 它把这张卡返回给 /token 接口。
def create_access_token(data: dict):
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Depends(oauth2_scheme): 一个聪明的助手。它会自动从你（客户端）的口袋里（HTTP 请求头）找出会员卡，然后递给保安。
#你（客户端） 向服务器的 /users/me 接口发起请求。这次，你很自觉地在请求头里出示了你的会员卡：Authorization: Bearer eyJhbGciOi...。
# 服务器的 /users/me 接口准备处理请求。但它看到门口站着一个保安 (get_current_user)，并且这个保安是通过 Depends() 这个依赖注入系统雇来的。
#   接口的定义看起来像这样: async def read_me(current_user: dict = Depends(get_current_user)):
#   FastAPI 看到 Depends，就知道：“哦，我必须先让这个保安工作，只有他放行了，我才能执行 read_me 的代码。”
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        token_data = {"username": username}
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    #现在，它终于可以执行 /users/me 接口的真正代码了，并且它会把保安返回的用户信息，作为 current_user 参数传递进去。
    return token_data