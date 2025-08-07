from sqlalchemy.orm import Session
from models import Todos
from pydantic import BaseModel

def create_todo(db: Session, todo_data: BaseModel):
    # 将 Pydantic 模型转换为 SQLAlchemy 模型
    new_todo = Todos(**todo_data.model_dump())
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)  # 刷新对象以获取数据库生成的值，如 id
    return new_todo

def get_todo_by_id(db: Session, todo_id: int):
    return db.query(Todos).filter(Todos.id == todo_id).first()

# 函数接收三个参数：
    # 1. db: 数据库会话，我们通过它与数据库交谈。
    # 2. todo_id: 要更新的那条 Todo 记录的 ID。
    # 3. todo_data: 一个 Pydantic 模型实例，包含了用于更新的【新数据】。
def update_todo(db: Session, todo_id: int, todo_data: BaseModel):
    todo_model = get_todo_by_id(db, todo_id)
    if todo_model is None:
        #    策略: 这个 CRUD 函数选择不直接抛出 HTTP 异常。它只是简单地返回 None。这是一种很好的分层设计：
        #          CRUD 层 (crud.py): 只负责数据库逻辑。它告诉调用者：“嘿，我没找到你要的东西。”
        #          路由层 (main.py): 接收到这个 None 的返回值后，由它来决定如何向客户端响应。它会负责将这个 None 翻译成一个 HTTP 404 Not Found 错误。
        return None 
    
    # 使用 Pydantic 模型的数据更新 SQLAlchemy 模型
    #todo_data.model_dump(): 将 Pydantic 模型 todo_data 转换为一个 Python 字典。例如：{'title': 'New Title', 'description': 'New Desc', ...}。
    for key, value in todo_data.model_dump().items():
        #todo_model.title = 'New Title'。
        setattr(todo_model, key, value)
        
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model


def delete_tode(db: Session , todo_id: int ):
    todo_to_delete = get_todo_by_id(db, todo_id)
    if todo_to_delete is None:
        return None
    
    db.delete(todo_to_delete)
    db.commit()
    print(todo_to_delete)
    return todo_to_delete
    