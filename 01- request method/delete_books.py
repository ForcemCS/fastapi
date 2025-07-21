from fastapi import FastAPI, HTTPException, status

from pydantic import BaseModel

from typing import List, Dict, Any, Optional


# 声明了一个继承自 Pydantic BaseModel 的类。这意味着 Book 类拥有了数据解析和验证的超能力。
# 可以post一个对象（一个对象 {...}）
class Book(BaseModel):
    title: str
    author: str
    category: str
    
class BookDelete(BaseModel):
    title: List[str]
    

app = FastAPI()


BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]


delete_books = {
  "title": [
    "Title One",
    "Title Three",
    "A book that does not exist"
  ]
}



@app.delete("/books/delete_books/", status_code=status.HTTP_200_OK)
async def delete_books(request: BookDelete):
    
    titles_delete_set =  {title.casefold() for title in request.title }
    
    
    books_keep= [
        book for book in BOOKS
        if book['title'].casefold() not  in  titles_delete_set
    ]
    
    delete_counts = len(BOOKS) - len(books_keep)
    
    if delete_counts == 0 :
        raise HTTPException (
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No books found with the provided titles: {request.title }"
        )

    BOOKS[:] = books_keep
    
    return {
        "message": "Books deleted successfully.",
        "deleted_count": delete_counts,
        "remaining_books": len(BOOKS)
    }



@app.get("/")
async def read_all_books():
    return BOOKS


