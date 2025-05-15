from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from ToDoApp.database import SessionLocal
from ToDoApp.models import Todos
from typing import Annotated
from .auth import get_current_user

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

router = APIRouter(
	prefix='/admin',
	tags=['admin']
)

@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
	if user.get('role') != "admin":
		raise HTTPException(status_code=401, detail="This enpoint is only accesible for admins")
	return db.query(Todos).all()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int):
	if user.get('role') != "admin":
		raise HTTPException(status_code=401, detail="This enpoint is only accesible for admins")
	todo = db.query(Todos).filter(Todos.id == todo_id).first()
	if todo is None:
		raise HTTPException(status_code=404, detail="Todo not found")
	db.delete(todo)
	db.commit()