from fastapi import FastAPI

from typing import List, Dict, Any, Optional

app = FastAPI()


BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]

@app.get("/")
async def read_all_books():
    return BOOKS

# @app.get("/books/{book_title}")      # path parameter  动态路径参数
# async def read_all_books(book_title: str):
#     # for book in BOOKS:
#     #     if book.get('title').casefold() == book_title.casefold():
#     #         return book
#     target_title = book_title.casefold() 
#     return next((book for book in BOOKS if book.get('title') and book.get('title').casefold() ==  target_title), '您找的书名不存在')


# 一个由字典组成的列表，字典的键必须是字符串，值
@app.get("/books/{author}", response_model=List[Dict[str, Any]])
# 如果用户提供了它，它的值应该是一个字符串；如果用户没提供，它的值默认为 None。”
async def filter_books(author: Optional[str] = None,category: Optional[str] = None):
    """
    根据作者和/或分类过滤书籍。
    - 如果提供了作者，按作者过滤。
    - 如果提供了分类，按分类过滤。
    - 如果两者都提供，则需要同时满足。
    """
    # 从完整的列表开始
    results = BOOKS

    if author:
        # 过滤作者
        target_author = author.casefold()
        # 注意：这里是在已有的 results 基础上继续过滤
        results = [book for book in results if book.get('author') and book.get('author').casefold() == target_author]  or [dict.fromkeys([target_author], 'does not exist')]

    if category:
        # 过滤分类
        target_category = category.casefold()
        results = [book for book in results if book.get('category') and book.get('category').casefold() == target_category]  or  [dict.fromkeys([target_category], ' does not exist')]
    
    return results
