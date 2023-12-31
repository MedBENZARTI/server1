from fastapi import APIRouter
from typing import Annotated, Union, List
from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import psycopg2
from fastapi import Depends, FastAPI, HTTPException, status
import pandas as pd
from datetime import datetime, timedelta, date
from typing import Annotated, Union, Optional 
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
    bikeId: Optional[int] = Field(None, gt=99999, lt=1000000)
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
    bikeModelYear: Optional[int] = Field(None, gt=2000, lt=3000)
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
class FormsToUpdate(BaseModel):
    # mandatory
    processIds: List[int]
    userFirstName: Union[str, None] = None
    userLastName: Union[str, None] = None 
    userEmail: Union[EmailStr, None] = None 
    userTelephone: Union[str, None] = None 
    userStreet: Union[str, None] = None 
    userHouseNumber: Union[str, None] = None 
    userZipCode: Union[str, None] = None 
    userCity: Union[str, None] = None 
    userCountry: Union[str, None] = None 
    bikeBrand: Union[str, None] = None 
    bikeModel: Union[str, None] = None 
    bikeRrp: Union[float, None] = None 
    bikeAccessories: Union[str, None] = None 
    bikeFrameNumber: Union[str, None] = None 
    contractStartDate: Union[date, None] = None 
    contractAmount: Union[float, None] = None 
    # optional
    pickDate: Union[date, None] = None
    bikeSize: Union[str, None] = None
    bikeId: Optional[int] = Field(None, gt=99999, lt=1000000)
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
    bikeModelYear: Optional[int] = Field(None, gt=2000, lt=3000)
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

async def read_data(sql):
    conn = psycopg2.connect(**DB_CON)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cols = [str(col[0]) for col in cur.description ]
    conn.close()
    return [dict(zip(cols, row)) for row in rows ]
    # return json.loads(pd.DataFrame(rows, columns=cols).to_json(orient = 'records'))

async def write_one(obj, table, returns = '*'):
    try:
        conn = psycopg2.connect(**DB_CON)
        cur = conn.cursor()
        keys = ', '.join([f'"{o}"' for o in obj.keys()])
        tags = ', '.join(['%s' for i in obj.values()])
        values = list(obj.values())
        sql = f"""
        Insert into {table} ({ keys }) values ({ tags })
        returning {returns}
        """
        cur.execute(sql, values)
        cols = [str(col[0]) for col in cur.description ]
        vals = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(zip(cols, vals))
    except (psycopg2.Error) as error:
        cur.close()
        conn.close()
        return False

async def insert_many(table: str, id_column: str, values: list):
    if not values:
        return []
    try:
        conn = psycopg2.connect(**DB_CON)
        cur = conn.cursor()
        keys = values[0].keys()
        query = cur.mogrify("INSERT INTO {} ({}) VALUES {} RETURNING {}".format(
                table,
                ', '.join([f'"{o}"' for o in keys]),
                ', '.join(['%s'] * len(values)),
                id_column
            ), [tuple(v.values()) for v in values])
        cur.execute(query)
        cols = [str(col[0]) for col in cur.description ]
        values = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return  [dict(zip(cols,val)) for val in values]
    except (psycopg2.Error) as error:
        cur.close()
        conn.close()
        return False
    
async def update_one(id, id_col, obj, table):
    try:
        conn = psycopg2.connect(**DB_CON)
        cur = conn.cursor()
        returns = ', '.join([f'"{o}"' for o in obj.keys()])
        to_update = ',\n'.join([f'''"{k}"=%s''' for k in obj])
        values = list(obj.values()) + [id]
        sql = f"""
        UPDATE {table} SET
        {to_update}
        where "{id_col}" = %s
        returning {returns}
        """
        print(sql)
        cur.execute(sql, values)
        cols = [str(col[0]) for col in cur.description ]
        vals = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(zip(cols, vals))
    except (psycopg2.Error) as error:
        print(error)
        cur.close()
        conn.close()
        return False

async def get_user(username: str):
    db = await read_data('select * from users')
    db = {o['username']:o for o in db}
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


@router.get("")
async def read_contracts(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    if current_user.role == 'admin':
        db = await read_data('select * from  public."Form"')
    else:
        db = await read_data(f"""select * from  public."Form" where "submittingUser" = '{current_user.username}' """)
    return {"data": db}

@router.post("/add")
async def add_ucontract(
    current_user: Annotated[User, Depends(get_current_active_user)],
    new_contracts: list[Form]
):
    obj = [{
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
    } for new_contract in new_contracts]
    
    con_created = await insert_many('public."Form"', '*',obj)
    return {
        'data': con_created
    }

@router.put("/update")
async def update_contract(
    current_user: Annotated[User, Depends(get_current_active_user)],
    updates: FormsToUpdate
):
    read_sql = """ select distinct "processId" from public."Form" """
    if current_user.role != 'admin':
        read_sql +=  f"""where "submittingUser" ='{current_user.username}' """
    current_users_contracts = [ o['processId'] for o in await read_data(read_sql)]
    not_available_ids = [str(id) for id in updates.processIds if id not in current_users_contracts]
    if not_available_ids != []:
        pid = ', '.join(not_available_ids)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"These processIds are not found: {pid}")
    updated = []
    not_updated = []
    for id in updates.processIds:
        try:
            keys_to_update = [ k for k,v in updates.__dict__.items() if v and k != 'processIds']
            enums = ['status', 'pickUpLogistics', 'bikeColor', 'contractCommunicationError', 'userGender', 'bikeType']
            obj = {
                k: updates.__dict__[k] if k not in enums else updates.__dict__[k].value
                for k in keys_to_update
            }
            updated_obj = await update_one(id, 'processId', obj, 'public."Form"')
            updated.append(updated_obj)
        except:
            not_updated.append(id)
    res = {
        'updated': updated,
        'not_updated': not_updated
    }
    return res