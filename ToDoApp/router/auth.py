from fastapi import APIRouter, status, Depends, HTTPException
from pydantic import BaseModel
from ToDoApp.models import Users
from passlib.context import CryptContext
from typing import Annotated
from ToDoApp.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from jose import jwt, JWTError

pw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

SECRET_KEY = 'dbe38197a5fd0dacb7c778bc5fbe3d70eb8f79a24dcb3440f92c86e6520f72aa'
ALGORITHM = 'HS256'

router = APIRouter(
	prefix='/auth',
	tags=['auth']
)

class CreateUserRequest(BaseModel):
	email: str
	username: str
	first_name: str
	last_name: str
	password: str
	role: str
	phone_number: str

class Token(BaseModel):
	access_token: str
	token_type: str

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username, password, db: db_dependency):
	user = db.query(Users).filter(Users.username == username).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	if not pw_context.verify(password, user.hashed_password):
		raise HTTPException(status_code=401, detail="Incorrect Password")
	return user

def create_acces_token(username: str, user_id: int, role: str, expires_delta: timedelta):
	encode = {"sub": username, "user_id": user_id, "role": role}
	expires = datetime.now(ZoneInfo("UTC")) + expires_delta
	encode.update({"exp": expires})
	return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def hash_password(password: str):
	return pw_context.hash(password)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
	try:
		payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
		username: str = payload.get('sub')
		user_id: int = payload.get('user_id')
		role: str = payload.get('role')
		if username is None or user_id is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user 1')
		return {'username': username, 'user_id': user_id, 'role': role}
	except JWTError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user 2')

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
	create_user_model = Users(
		email=create_user_request.email,
		username=create_user_request.username,
		first_name=create_user_request.first_name,
		last_name=create_user_request.last_name,
		hashed_password=pw_context.hash(create_user_request.password),
		role=create_user_request.role,
		is_active=True,
		phone_number = create_user_request.phone_number
	)

	db.add(create_user_model)
	db.commit()

@router.post("/token", response_model=Token)
async def get_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
	user = authenticate_user(form_data.username, form_data.password, db)
	token = create_acces_token(user.username, user.id, user.role, timedelta(minutes=30))
	return {"access_token": token, "token_type": "bearer"}
