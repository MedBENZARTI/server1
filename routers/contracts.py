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

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Gender(str, Enum):
    Mr = "Mr"
    Mrs = "Mrs"
    Other = "Other"


class Status(str, Enum):
    Open = 'Open'
    Paid = 'Paid'
    Invoiced = 'Invoiced'
    Completed = 'Completed'
    Waiting = 'Waiting'
    ReadyToInvoice = 'ReadyToInvoice'
    InboundCheck = 'InboundCheck'
    Received = 'Received'
    PickedUp = 'PickedUp'
    InPickUp = 'InPickUp'
    Avis = 'Avis'
    Canceled = 'Canceled'
    Reapply = 'Reapply'
    PickUpFailed = 'PickUpFailed'


class PickUpLogistics(str, Enum):
    Wiechert = 'Wiechert'
    Emons = 'Emons'
    Gaehler = 'Gaehler'
    Alltrans = 'Alltrans'

class Bike(str, Enum):
    Bicycle = 'Bicycle'
    Pedelec = 'Pedelec'
    Other = 'Other'

class Color(str, Enum):
    Yellow = 'Yellow'
    Gold = 'Gold'
    Organe = 'Organe'
    Red = 'Red'
    Pink = 'Pink'
    Purple = 'Purple'
    Blue = 'Blue'
    Turquoise = 'Turquoise'
    Green = 'Green'
    Grey = 'Grey'
    Brown = 'Brown'
    Copper = 'Copper'
    White = 'White'
    Black = 'Black'
    Silver = 'Silver'
    Multicolor = 'Multicolor'

class communicationError(str, Enum):
    Bounced = 'Bounced'
    IncorrectPhone = 'IncorrectPhone'
    none = 'None'

class userRole(str, Enum):
    BackendUserLeasing = 'BackendUserLeasing'
    FrontUser = 'FrontUser'
    SuperBackendUser = 'SuperBackendUser'
    BackendUserCustomerCare = 'BackendUserCustomerCare'
    BackendUserLogisticsWI = 'BackendUserLogisticsWI'
    BackendUserLogisticsEM = 'BackendUserLogisticsEM'
    BackendUserLogisticsGA = 'BackendUserLogisticsGA'
    BackendUserLogisticsAT = 'BackendUserLogisticsAT'

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
    contractStartDate: date
    contractAmount: float
    # optional
    pickDate: Union[date, None] = None
    bikeSize: Union[str, None] = None
    bikeId: Union[int, None] = None
    contractSettlementPrice: Union[float, None] = None
    contractSettlementDate: Union[date, None] = None
    status: Union[Status, None] = None
    pickUpLogistics: Union[PickUpLogistics, None] = None
    statusComment: Union[str, None] = None
    contractNumber: Union[str, None] = None
    pickUpFeedback: Union[str, None] = None
    bikeAdditionalText: Union[str, None] = None
    bikeBatteryNumber: Union[str, None] = None
    bikeColor: Union[Color, None] = None
    bikeKind: Union[str, None] = None
    bikeModelYear: Union[int, None] = None
    bikeOriginalPurchasePrice: Union[float, None] = None
    bikeOriginalPurchasePriceNet: Union[float, None] = None
    bikeUser: Union[str, None] = None
    contractAttachment: Union[str, None] = None
    contractCommunicationError: Union[communicationError, None] = None
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
    userGender: Union[Gender, None] = None
    userMobilePhone: Union[str, None] = None
    bikeType: Union[Bike, None] = None

class FormInDB(Form):
    submittingUser: str

class User(BaseModel):
    username: str
    email: EmailStr
    role: str # Role
    name: Union[str, None] = None
    disabled: Union[bool, None] = None

class UserInReq(User):
    password: str

class UserInDB(UserInReq):
    id: int

class TokenData(BaseModel):
    username: Union[str, None] = None

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
    return json.loads(pd.DataFrame(rows, columns=cols).to_json(orient = 'records'))

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

async def get_user(username: str):
    db = await read_data('select * from users')
    db = {o['username']:o for o in db}
    print(db)
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

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

'''
@router.post("/contracts/add/")
async def add_ucontract(
    current_user: Annotated[User, Depends(get_current_active_user)],
    new_contract: Form
):
    obj = new_contract.__dict__
    obj['submittingUser'] = current_user.username
    insert_query = f"""INSERT INTO public."Form" ("{'", "'.join(obj.keys())}") VALUES ({', '.join([format_value_for_sql(v) for v in obj.values()])})"""
    print(insert_query)
    q = await write_one(insert_query)
    return q
'''

@router.get("")
async def read_contracts(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    db = await read_data('select * from  public."Form"')
    return {"data": db}

@router.post("/contracts/add/")
async def add_ucontract(
    current_user: Annotated[User, Depends(get_current_active_user)],
    new_contract: Form
):
    obj = {
        'submittingUser' : current_user.username,
        'userFirstName' : new_contract.userFirstName,
        'userLastName' : new_contract.userLastName,
        'userEmail' : new_contract.userEmail,
        'userTelephone' : new_contract.userTelephone,
        'userStreet' : new_contract.userStreet,
        'userHouseNumber' : new_contract.userHouseNumber,
        'userZipCode' : new_contract.userZipCode,
        'userCity' : new_contract.userCity,
        'userCountry' : new_contract.userCountry,
        'bikeBrand' : new_contract.bikeBrand,
        'bikeModel' : new_contract.bikeModel,
        'bikeRrp' : new_contract.bikeRrp,
        'bikeAccessories' : new_contract.bikeAccessories,
        'bikeFrameNumber' : new_contract.bikeFrameNumber,
        'contractStartDate' : new_contract.contractStartDate,
        'contractAmount' : new_contract.contractAmount,
        'pickDate' : new_contract.pickDate,
        'bikeSize' : new_contract.bikeSize,
        'bikeId' : new_contract.bikeId,
        'contractSettlementPrice' : new_contract.contractSettlementPrice,
        'contractSettlementDate' : new_contract.contractSettlementDate,
        'status' : new_contract.status.value,
        'pickUpLogistics' : new_contract.pickUpLogistics.value,
        'statusComment' : new_contract.statusComment,
        'contractNumber' : new_contract.contractNumber,
        'pickUpFeedback' : new_contract.pickUpFeedback,
        'bikeAdditionalText' : new_contract.bikeAdditionalText,
        'bikeBatteryNumber' : new_contract.bikeBatteryNumber,
        'bikeColor' : new_contract.bikeColor.value,
        'bikeKind' : new_contract.bikeKind,
        'bikeModelYear' : new_contract.bikeModelYear,
        'bikeOriginalPurchasePrice' : new_contract.bikeOriginalPurchasePrice,
        'bikeOriginalPurchasePriceNet' : new_contract.bikeOriginalPurchasePriceNet,
        'bikeUser' : new_contract.bikeUser,
        'contractAttachment' : new_contract.contractAttachment,
        'contractCommunicationError' : new_contract.contractCommunicationError.value,
        'contractConditionBasedReduction' : new_contract.contractConditionBasedReduction,
        'contractDeliveryInformation' : new_contract.contractDeliveryInformation,
        'contractPartsBasedReduction' : new_contract.contractPartsBasedReduction,
        'contractPartsMissing' : new_contract.contractPartsMissing,
        'contractSentToLogistics' : new_contract.contractSentToLogistics,
        'contractStateChangedDate' : new_contract.contractStateChangedDate,
        'contractSubmitDate' : new_contract.contractSubmitDate,
        'pickContractReceived' : new_contract.pickContractReceived,
        'pickEarliest' : new_contract.pickEarliest,
        'pickTimeFrom' : new_contract.pickTimeFrom,
        'pickTimeTill' : new_contract.pickTimeTill,
        'pickUpOkay' : new_contract.pickUpOkay,
        'userCompany' : new_contract.userCompany,
        'userDeviatingPickup' : new_contract.userDeviatingPickup,
        'userDeviatingPickupAddress' : new_contract.userDeviatingPickupAddress,
        'userFederalState' : new_contract.userFederalState,
        'userFunction' : new_contract.userFunction,
        'userGender' : new_contract.userGender.value,
        'userMobilePhone' : new_contract.userMobilePhone,
        'bikeType' : new_contract.bikeType.value
    }
    insert_query = f"""INSERT INTO public."Form" ("{'", "'.join(obj.keys())}") VALUES ({', '.join([format_value_for_sql(v) for v in obj.values()])})"""
    q = await write_one(insert_query)
    return q