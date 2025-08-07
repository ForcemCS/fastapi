from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends,HTTPException, status,Path
from pydantic import BaseModel, Field
import models
import crud 
from models import Todos
from database import engine, SessionLocal # 从 database.py 导入我们创建的那个数据库引擎

        
app = FastAPI()


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Test Data",
                "description": "learn fastAPI",
                "priority": 4,
                "complete": False
            }
        }
    }

# 这是至关重要的一步，它将前面所有部分连接了起来：
# - `models.Base`: 我们访问到 `models.py` 文件中所有继承自 `Base` 的类（即 `Users` 和 `Todos`）。
# - `.metadata`: `Base` 有一个特殊的属性 `metadata`，它像一个注册表，收集了所有这些模型的信息（表名、列、关系等）。
# - `.create_all(bind=engine)`: 这个方法会告诉 `metadata`：“请检查 `engine` 连接的那个数据库，把你注册的所有表（如果它们还不存在的话）都创建出来。”
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()  # 1. 创建一个数据库会话, 从database.py 里的 SessionLocal会话工厂，取出一个全新的、干净的数据库会话 db
    try:

        yield db         # 2. “产出”或“提供”这个会话， 程序执行到这里会暂停，然后把 db 对象“注入”到需要它的地方（比如我们的 API 路由函数）。
    finally:
        db.close()       # 3. 当依赖 get_db 的代码（也就是我们的 API 路由函数）执行完毕后，无论是成功返回了结果，还是中途发生了错误，程序的控制权都会回到 yield db 暂停的地方。然后，程序继续向下执行，进入 finally 块。

# FastAPI 的执行流程：
# 当一个客户端请求访问服务器的根路径 / 时，FastAPI 会做以下事情：

# 步骤 A: FastAPI 看到 read_all 函数需要一个名为 db 的参数，并且这个参数依赖于 get_db。
# 步骤 B: FastAPI 自动调用 get_db()。
# 步骤 C: get_db() 执行到 yield db，创建并产出一个数据库会话对象。
# 步骤 D: FastAPI 接收到这个 db 对象，然后将它作为参数传递给 read_all 函数。就像这样调用：read_all(db=那个新鲜的会话对象)。
# 步骤 E: read_all 函数内部的代码开始执行。现在，函数体内的 db 就是一个可用的、活跃的数据库会话。
# 步骤 F: return db.query(Todos).all() 执行。它使用这个会话 db 向数据库查询 Todos 表中的所有记录，并返回结果。
# 步骤 G: read_all 函数执行完毕。FastAPI 知道它完成了。
# 步骤 H: FastAPI 回到 get_db 函数暂停的地方，让它继续执行。
# 步骤 I: get_db 函数执行 finally 块中的 db.close()，安全地关闭了会话。


db_dependency =  Annotated[Session, Depends(get_db)]

@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo_route(db: db_dependency, to_request: TodoRequest):
    crud.create_todo(db=db, todo_data=to_request)
    # 你甚至可以返回创建的对象，如果你在 crud 函数中 return 的话

@app.put("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo_route(db: db_dependency, id: int, todo_request: TodoRequest):
    updated_todo = crud.update_todo(db=db, todo_id=id, todo_data=todo_request)
    if updated_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')
    

@app.get("/")
#db: Session 是一个类型提示。它告诉你的编辑器（如 VS Code）和代码检查工具：“db 这个变量的类型是 SQLAlchemy 的 Session”。这能给你带来非常好的代码自动补全和类型检查功能。当你输入 db. 时，编辑器就会智能地提示你 query(), add(), commit() 等方法。
#Annotated[Session, Depends(get_db)] 是 Python 3.9+ 引入的一种更清晰的类型提示方式，它能将类型信息（Session）和 FastAPI 的元数据（Depends）优雅地结合在一起。功能上和 db: Session = Depends(get_db) 完全一样。

# async def read_all(db: Annotated[Session, Depends(get_db)]):
async def read_all(db: Annotated[Session, Depends(get_db)]):
    return db.query(Todos).all()


@app.get("/todo/{id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, id: int = Path(gt=0) ):
    #如果数据库返回了任何结果，请把第一行数据转换成一个 Todos 的 Python 对象实例，然后返回给我。”
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    
    if todo_model:
        return todo_model
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='todo id not found')

