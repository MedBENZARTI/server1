from datetime import datetime, timedelta, date
from typing import Annotated, Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from enum import Enum
import psycopg2
import pandas as pd


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DB_CON = {
        "host"      : 'rds-ticket-app-prod.czgosi3nm3l7.eu-central-1.rds.amazonaws.com',
        "database"  : 'public',
        "user"      : 'ticketappuser',
        "password"  : 'GA8yDbApaTthvqgH16V0jg==',
        'port'      : '5432'
    }

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

async def read_data(sql):
    conn = psycopg2.connect(**DB_CON)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cols = [str(col[0]) for col in cur.description ]
    conn.close()
    return pd.DataFrame(rows, columns=cols).to_dict('records')

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


fake_users_db = {
    "johndoe": {
        "id": 5,
        "username": "johndoe",
        "name": "John Doe",
        "email": "johndoe@example.com",
        "role": "admin",
        "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "simon": {
        "id": 4,
        "username": "simon",
        "name": "Simon Heinken",
        "email": "simon@example.com",
        "role": "user",
        "password": "$2b$12$Uw24ZOUFR0Cm5m29zv64bu1TQN9z9UbHBQAvAWnh2gVdpygEkMETa",
        "disabled": False,
    },
    "mohamed": {
        "id": 6,
        "username": "mohamed",
        "name": "mohamed benz",
        "email": "mohamed@example.com",
        "role": "admin",
        "password": "$2b$12$P2pFehGdRpyLW574cMBeXeVtxYdSIlK6u/n2tJQMR6XDNT3i66rUO",
        "disabled": False,
    }
}

class Role(str, Enum):
    admin = "admin"
    user = "user"
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

class Form(BaseModel):
    # mandatory
    userFirstName: str
    userLastName: str 
    userEmail: EmailStr
    userTelephone: str
    userStreet: str
    userHouseNumber: str
    userZipCode: str
    userCity: str
    userCountry: str
    bikeBrand: str
    bikeModel: str
    bikeRrp: float
    bikeAccessories: str
    bikeFrameNumber: str
    contractStartDate: str
    contractAmount: float
    # optional
    pickDate: Union[date, None] = None
    bikeSize: Union[str, None] = None
    bikeId: Union[int, None] = None
    contractSettlementPrice: Union[float, None] = None
    contractSettlementDate: Union[date, None] = None
    status: Union[str, None] = None
    pickUpLogistics: Union[str, None] = None
    statusComment: Union[str, None] = None
    contractNumber: Union[str, None] = None
    pickUpFeedback: Union[str, None] = None
    bikeAdditionalText: Union[str, None] = None
    bikeBatteryNumber: Union[str, None] = None
    bikeColor: Union[str, None] = None
    bikeKind: Union[str, None] = None
    bikeModelYear: Union[int, None] = None
    bikeOriginalPurchasePrice: Union[float, None] = None
    bikeOriginalPurchasePriceNet: Union[float, None] = None
    bikeUser: Union[str, None] = None
    contractAttachment: Union[str, None] = None
    contractCommunicationError: Union[str, None] = None
    contractConditionBasedReduction: Union[float, None] = None
    contractDeliveryInformation: Union[str, None] = None
    contractPartsBasedReduction: Union[float, None] = None
    contractPartsMissing: Union[str, None] = None
    contractSentToLogistics: Union[bool, None] = None
    contractStateChangedDate: Union[date, None] = None
    contractSubmitDate: Union[date, None] = None
    pickContractReceived: Union[bool, None] = None
    pickEarliest: Union[date, None] = None
    pickTimeFrom: Union[str, None] = None
    pickTimeTill: Union[str, None] = None
    pickUpOkay: Union[bool, None] = None
    userCompany: Union[str, None] = None
    userDeviatingPickup: Union[bool, None] = None
    userDeviatingPickupAddress: Union[str, None] = None
    # userEmailId: Union[str, None] = None
    userFederalState: Union[str, None] = None
    userFunction: Union[str, None] = None
    userGender: Union[str, None] = None
    userMobilePhone: Union[str, None] = None
    bikeType: Union[str, None] = None

class FormInDB(Form):
    submittingUser: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)

def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
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
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
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


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user

@app.post("/users/new/")
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
        "role": new_user.role,
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
    return await read_data(f"""select id,username,email,"role","name",disabled from Users where username = '{new_user.username}'""")


@app.post("/contracts/add/")
async def add_ucontract(
    current_user: Annotated[User, Depends(get_current_active_user)],
    new_contract: Form
):
    obj = new_contract.__dict__
    obj['submittingUser'] = current_user.username
    insert_query = f"""INSERT INTO form ("{"', '".join(obj.keys())}") VALUES ({', '.join([format_value_for_sql(v) for v in obj.values()])})"""
    print(insert_query)
    q = await write_one(insert_query)
    return q

@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]
