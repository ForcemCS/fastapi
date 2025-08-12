from __future__ import annotations
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase

from database import Base


# class Users(Base):
#     __tablename__ = 'users'

#     # 使用 Mapped 和 mapped_column，类型提示更清晰
#     id: Mapped[int] = mapped_column(primary_key=True, index=True)
#     email: Mapped[str] = mapped_column(String, unique=True)
#     username: Mapped[str] = mapped_column(String, unique=True)
#     first_name: Mapped[str] = mapped_column(String)
#     last_name: Mapped[str] = mapped_column(String)
#     hashed_password: Mapped[str] = mapped_column(String)
#     is_active: Mapped[bool] = mapped_column(Boolean, default=True)
#     role: Mapped[str] = mapped_column(String)
    
#     # 3. 添加 relationship 属性，并提供清晰的类型提示
#     # 它告诉我们 user.todos 将是一个包含 Todos 对象的列表
#     todos: Mapped[list["Todos"]] = relationship(back_populates="owner")

#     def __repr__(self):
#         return f"<User(id={self.id}, username='{self.username}', is_active={self.is_active})>"

# # 4. 定义 Todos 模型 (现代风格)
# class Todos(Base):
#     __tablename__ = 'todos'

#     id: Mapped[int] = mapped_column(primary_key=True, index=True)
#     title: Mapped[str] = mapped_column(String)
#     description: Mapped[str] = mapped_column(String)
#     priority: Mapped[int] = mapped_column(Integer)
#     complete: Mapped[bool] = mapped_column(Boolean, default=False)
    
#     # ForeignKey 的定义方式保持不变，但用 mapped_column 包装
#     owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
#     # 5. 添加对应的 relationship，完成双向绑定
#     # 它告诉我们 todo.owner 将是一个 Users 对象
#     owner: Mapped["Users"] = relationship(back_populates="todos")
    
#     def __repr__(self):
#         return f"<Todo(id={self.id}, title='{self.title}')>"




# 定义 User 模型，它将映射到数据库中的 'users' 表
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True) 
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    
    # 一个友好的字符串表示，方便打印对象
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', is_active='{self.is_active}')>"

print("User 模型定义成功！")


# 定义 Todos 模型，它将映射到数据库中的 'todos' 表
class Todos(Base):            # <--- 关键点 1：继承了魔法基类，当 Todos 类继承了 Base（那个通过 declarative_base() 创建的类）时，SQLAlchemy 的内部机制就被激活了。
    __tablename__ = 'todos'   # <--- 关键点 2：明确的映射关系，“我，Python 类 Todos，从现在起，全权代表数据库中的那张名为 'todos' 的表。所有对我这个类的操作，都请你翻译成对那张表的操作。”
    # 定义表的列 
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))   #alices_todos = db.query(Todos).filter(Todos.owner_id == 1).all()   查询语句有一定的局限性
    
    def __repr__(self):
        return f"<User(id={self.id}, title='{self.title}'')>"

# SQLAlchemy 在内部维护了一个“注册表”（就是我们之前提到的 Base.metadata），里面记录了所有这些映射关系：

# Users 类 -> 'users' 表
# Todos 类 -> 'todos' 表
# Todos.id 属性 -> 'todos' 表的 id 列
# Todos.title 属性 -> 'todos' 表的 title 列
# 等等...
