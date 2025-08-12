from fastapi import FastAPI, Depends,HTTPException, status,Path
import models
import crud 
from database import engine, SessionLocal # 从 database.py 导入我们创建的那个数据库引擎
from routers import auth, todos

app = FastAPI()

# 步骤 2: 将 auth 路由模块“包含”到主应用中
app.include_router(
    auth.router, 
    prefix="/auth",
    tags=["Authentication"] 
)

app.include_router(
    todos.router, 
    tags=["Todos"]
)


# 这是至关重要的一步，它将前面所有部分连接了起来：
# - `models.Base`: 我们访问到 `models.py` 文件中所有继承自 `Base` 的类（即 `Users` 和 `Todos`）。
# - `.metadata`: `Base` 有一个特殊的属性 `metadata`，它像一个注册表，收集了所有这些模型的信息（表名、列、关系等）。
# - `.create_all(bind=engine)`: 这个方法会告诉 `metadata`：“请检查 `engine` 连接的那个数据库，把你注册的所有表（如果它们还不存在的话）都创建出来。”
models.Base.metadata.create_all(bind=engine)