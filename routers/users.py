from fastapi import APIRouter
from typing import Annotated, Union
from pydantic import BaseModel, EmailStr
from enum import Enum
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import psycopg2
from fastapi import Depends, FastAPI, HTTPException, status
import pandas as pd
from datetime import datetime, timedelta, date
from typing import Annotated, Union
from jose import JWTError, jwt
import json



DB_CON = {
        "host"      : 'rds-ticket-app-prod.czgosi3nm3l7.eu-central-1.rds.amazonaws.com',
        "database"  : 'public',
        "user"      : 'ticketappuser',
        "password"  : 'GA8yDbApaTthvqgH16V0jg==',
        'port'      : '5432'
    }

router = APIRouter()

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Role(str, Enum):
    user = "user"
    admin = "admin"
class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    username: Union[str, None] = None
class User(BaseModel):
    username: str
    email: EmailStr
    role: Role
    name: Union[str, None] = None
    disabled: Union[bool, None] = None

class UserInReq(User):
    password: str

class UserInDB(UserInReq):
    id: int

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def format_value_for_sql(value):
    if value is None:
        return "NULL"
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        return str(value)
    elif isinstance(value, bool):
        return str(int(value))  # Convert bool to 0 or 1
    else:
        # If the data type is not recognized, raise an error or handle it accordingly
        return f"""'{str(value).replace("'", "''")}'"""
    
async def write_one(sql):
    try:
        conn = psycopg2.connect(**DB_CON)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    except (Exception, psycopg2.Error) as error:
        return {'error': error.__dict__}
    conn.close
    return 1

async def read_data(sql):
    conn = psycopg2.connect(**DB_CON)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cols = [str(col[0]) for col in cur.description ]
    conn.close()
    return json.loads(pd.DataFrame(rows, columns=cols).to_json(orient = 'records'))


def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_user(username: str):
    db = await read_data('select * from users')
    db = {o['username']:o for o in db}
    print(db)
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    
async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    print(current_user)
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user

@router.post("/users/new/")
async def add_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    new_user: UserInReq
):
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have permission to do this action",
        )
    obj = {
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role.value,
        "name": new_user.name,
        "password": pwd_context.hash(new_user.password),
        "disabled": new_user.disabled
        }

    usernames = await read_data('select distinct username from users')
    if new_user.username in [o['username'] for o in usernames]:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="username already exists!",
            )
    insert_query = f"INSERT INTO users ({', '.join(obj.keys())}) VALUES ({', '.join([format_value_for_sql(v) for v in obj.values()])})"
    
    await write_one(insert_query)
    return await read_data(f"""select id,username,email,"role","name",
    disabled from Users where username = '{new_user.username}'""")

@router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]

@router.get("/users/all")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    db = await read_data('select * from users')
    db = {o['username']:o for o in db}
    return [{"data": db}]