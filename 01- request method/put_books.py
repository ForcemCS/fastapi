from fastapi import FastAPI, HTTPException, status

from pydantic import BaseModel

from typing import List, Dict, Any, Optional

# 声明了一个继承自 Pydantic BaseModel 的类。这意味着 Book 类拥有了数据解析和验证的超能力。
# 可以post一个对象（一个对象 ({...})）
class Book(BaseModel):
    title: str
    author: str
    category: str
    
    
app = FastAPI()


BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]


test_put = [
    {
        "title": "Title One",
        "author": "Author A",
        "category": "category put A "
    },
    {
        "title": "Title Two",
        "author": "Author B",
        "category": "category put B"
    }
]





@app.put("/books/update_books")
async def update_books(books_to_update: List[Book]):
    # 在每次迭代中，变量 book 成为一个指向 BOOKS 列表中某个字典对象的引用。
    # books_db_map 的值集合，就是指向 BOOKS 列表中那些原始字典对象的引用集合。这里没有创建任何新的书籍字典。
    books_db_map = {book.get('title').casefold(): book for book in BOOKS}
    
    updated_count = 0
    not_found_titles = []

    # 遍历传入的待更新书籍列表
    for book_update in books_to_update:
        # 找到要更新的原始条目
        # #当匹配成功时，book_to_modify 这个变量现在也获得了对原始字典的引用。
        book_to_modify = books_db_map.get(book_update.title.casefold())
        

        if book_to_modify:
            # .model_dump() 将 Pydantic 对象转为字典
            book_to_modify.update(book_update.model_dump())
            updated_count += 1
        else:
            # 没找到，记录下来
            not_found_titles.append(book_update.title)

    # 构建清晰的响应报告
    response_message = f"Operation finished. Updated: {updated_count}, Not Found: {len(not_found_titles)}."
    
    # 如果所有书都没找到，可以考虑返回 404
    if updated_count == 0 and not_found_titles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": response_message, "not_found": not_found_titles}
        )
        
    return {
        "message": response_message,
        "updated_count": updated_count,
        "not_found": not_found_titles
    }



@app.get("/")
async def read_all_books():
    return BOOKS


