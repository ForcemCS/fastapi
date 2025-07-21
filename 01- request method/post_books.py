from fastapi import FastAPI

from pydantic import BaseModel

from typing import List, Dict, Any, Optional

# 声明了一个继承自 Pydantic BaseModel 的类。这意味着 Book 类拥有了数据解析和验证的超能力。
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


@app.post("/books/create_book")
# create_book 函数需要一个 Book 类型的参数
async def create_book(new_book: Book): 
    BOOKS.append(new_book.dict())
    return {"message": "Book created successfully", "book": new_book}


@app.get("/")
async def read_all_books():
    return BOOKS