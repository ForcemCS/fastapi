BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'}
]


for book in BOOKS:
    print(book['title'])  # 使用方括号和字符串键名 'title'


# ===== 辅助理解 =====
# class Book:
#     def __init__(self, title: str, author: str, category: str):
#        
#         self.title = title
#         self.author = author
#         self.category = category



from pydantic import BaseModel

# 首先需要定义 Book 模型
class Book(BaseModel):
    title: str
    author: str
    category: str

# 原始的字典列表
BOOKS_DATA = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'}
]

# 将字典列表 转换成 Book 对象列表
# Book(**data) 是一个Python 技巧，它将字典解包成关键字参数
# Book(**{'title': 'T1', ...}) 等价于 Book(title='T1', ...)
book_objects = [Book(**data) for data in BOOKS_DATA]

# 现在，book 是一个 Book 对象了！
for book in book_objects:

    print(book.title)