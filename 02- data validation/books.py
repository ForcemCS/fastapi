from fastapi  import FastAPI,HTTPException, status

from pydantic import BaseModel, Field

from typing import List, Dict, Optional, Any

app = FastAPI()

class Book(BaseModel):
    id: int
    title: str
    author: str
    description: str
    rating: int = Field(gt=0 , lt=6)   # 添加校验：评分必须在1到5之间
        
BOOKS = [
    Book(id=1, title='Computer Science Pro', author='codingwithroby', description='A very nice book!', rating=5),
    Book(id=2, title='Be Fast with FastAPI', author='codingwithroby', description='A great book!', rating=5),
    Book(id=3, title='Master Endpoints', author='codingwithroby', description='A awesome book!', rating=5),
    Book(id=4, title='HP1', author='Author 1', description='Book Description', rating=2),
    Book(id=5, title='HP2', author='Author 2', description='Book Description', rating=3),
    Book(id=6, title='HP3', author='Author 3', description='Book Description', rating=1)
]


@app.get("/books")
async def read_all_books():
    return BOOKS

@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
# 将post的json文本转换为py中的字典，并进行验证，通过后就是一个Book对象
async def create_book(book_request: Book):
    new_id = BOOKS[-1].id  + 1 if BOOKS else 1 
    
    book_request.id = new_id
    
    BOOKS.append(book_request)
    
    return book_request