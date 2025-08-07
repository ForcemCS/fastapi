from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

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
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    def __repr__(self):
        return f"<User(id={self.id}, title='{self.title}'')>"

# SQLAlchemy 在内部维护了一个“注册表”（就是我们之前提到的 Base.metadata），里面记录了所有这些映射关系：

# Users 类 -> 'users' 表
# Todos 类 -> 'todos' 表
# Todos.id 属性 -> 'todos' 表的 id 列
# Todos.title 属性 -> 'todos' 表的 title 列
# 等等...
