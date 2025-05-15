from fastapi import Depends, HTTPException, status, Path, APIRouter
from sqlalchemy.orm import Session
from ToDoApp.database import SessionLocal
from ToDoApp.models import Users
from typing import Annotated
from pydantic import BaseModel, StringConstraints
from .auth import get_current_user, authenticate_user, hash_password
from typing import Annotated

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

router = APIRouter(
	prefix='/users',
	tags=['users']
)

class PasswordUpdate(BaseModel):
	current_password: str
	new_password: str

class PhoneNumberUpdate(BaseModel):
	new_phone_number: Annotated[str, StringConstraints(min_length=10, max_length=10)]

	class Config:
		json_schema_extra = {
			"example": {
				"new_phone_number": "0612345678"
			}
		}

@router.get("/current_user", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
	current_user = db.query(Users).filter(Users.id == user.get('user_id')).first()
	return current_user

@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, pw_request: PasswordUpdate):
	user = authenticate_user(user.get('username'), pw_request.current_password, db)
	user.hashed_password = hash_password(pw_request.new_password)
	db.add(user)
	db.commit()

@router.put("/change_phone_number", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, new_phone_number_request: PhoneNumberUpdate):
	current_user = db.query(Users).filter(Users.id == user.get('user_id')).first()
	current_user.phone_number = new_phone_number_request.new_phone_number
	db.add(current_user)
	db.commit()