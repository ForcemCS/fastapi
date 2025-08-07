from sqlalchemy import create_engine, Column, Integer, String
#与数据库的所有交互都是通过 Session (会话)进行的。可以把 Session 看作是与数据库进行对话的临时工作区。
#数据模型是数据库中表的 Python 表示。我们使用 SQLAlchemy 的 Declarative Base 来定义模型。
from sqlalchemy.orm import declarative_base, sessionmaker

# 创建数据库引擎
DATABASE_URL = "sqlite:///./todos.db"
#connect_args` 是一个特殊配置，专门用于 SQLite，以解决多线程访问的问题，这在像 FastAPI 这样的 Web 应用中是必需的。
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# autocommit=False 和 autoflush=False 是推荐的设置，让你能更好地控制事务。
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 5. 创建一个“模型基类” (Declarative Base)
Base = declarative_base()
# `declarative_base()` 返回一个类 `Base`。
# 这个 `Base` 类非常特殊，它将成为我们所有数据库模型（比如用户模型、待办事项模型）的父类。
# 继承了 `Base` 的类，SQLAlchemy 就能自动将它们识别为数据库表模型，并进行映射。
# 把它想象成一个“魔法”基类，它能让你的普通 Python 类变成数据库表。


