from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status

app = FastAPI()

class Book:
	id: int
	title: str
	author: str
	description: str
	rating: int
	published_date: int

	def __init__(self, id, title, author, description, rating, published_date):
		self.id = id
		self.title = title
		self.author = author
		self.description = description
		self.rating = rating
		self.published_date = published_date

class BookRequest(BaseModel):
	id: Optional[int] = Field(description="ID is not neeeded upon creation", default=None)
	title: str = Field(min_length=3)
	author: str = Field(min_length=1)
	description: str = Field(min_length=1, max_length=100)
	rating: int = Field(gt=-1, lt= 6)
	published_date: int = Field(gt=-1, lt=2026)

	model_config = {
		"json_schema_extra": {
			"example": {
				"title": "A new book",
				"author": "George Droid",
				"description": "A new description of a book",
				"rating": 5
			}
		}
	}

BOOKS = [
	Book(1, 'Computer Science Pro', 'George Droid', 'Learn to code!', 4, 2021),
	Book(2, 'Be fast with FastAPI', 'Remco van der Doorn', 'A great book!', 5, 2024),
	Book(3, 'Master endpoints', 'codingwithroby', 'Land a job in 2 weeks', 3, 2003),
	Book(4, 'Book1', 'Author1', 'book description', 1, 1987),
	Book(5, 'Book2', 'Author2', 'book description', 2, 2012)
]

@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
	return BOOKS

@app.get("/books/{id}", status_code=status.HTTP_200_OK)
async def get_book_by_id(id: int = Path(gt=0)):
	for book in BOOKS:
		if book.id == id:
			return book
	raise HTTPException(status_code=404, detail='Item not found')

@app.get("/books/", status_code=status.HTTP_200_OK)
async def filter_books_by_rating(rating: int = Query(gt=0, lt=6)):
	books_to_return = []
	for book in BOOKS:
		if book.rating == rating:
			books_to_return.append(book)
	return books_to_return

#since only published dat is updated it will not go through pydantics BaseModel. So repeat any checks for single parameters
@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def filter_by_published_date(published_date: int = Query(gt=-1, lt=2026)):
	books_to_return = []
	for book in BOOKS:
		print(book.published_date, published_date)
		if book.published_date == published_date:
			books_to_return.append(book)
	return books_to_return

@app.post("/add-book", status_code=status.HTTP_201_CREATED)
async def add_book(book_request: BookRequest):
	new_book = Book(**book_request.model_dump())
	calculate_new_book_id(new_book)
	BOOKS.append(new_book)

def calculate_new_book_id(new_book: Book):
	new_book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1

@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book_request: BookRequest):
	for i in range(len(BOOKS)):
		if BOOKS[i].id == book_request.id:
			BOOKS[i] = Book(**book_request.model_dump())
			return
	raise HTTPException(status_code=404, detail='item not found')
	

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
	for i in range(len(BOOKS)):
		if BOOKS[i].id == book_id:
			BOOKS.pop(i)
			return
	raise HTTPException(status_code=404, description='item not found')
