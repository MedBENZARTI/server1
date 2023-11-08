from typing import Annotated, Union
from pydantic import BaseModel, EmailStr
from enum import Enum
from fastapi import Depends, FastAPI
from datetime import date
from typing import Annotated, Union
from pydantic import BaseModel, EmailStr
from enum import Enum
from routers import  users



DB_CON = {
        "host"      : 'rds-ticket-app-prod.czgosi3nm3l7.eu-central-1.rds.amazonaws.com',
        "database"  : 'public',
        "user"      : 'ticketappuser',
        "password"  : 'GA8yDbApaTthvqgH16V0jg==',
        'port'      : '5432'
    }






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
    none = 'None'
    Bounced = 'Bounced'
    IncorrectPhone = 'IncorrectPhone'

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
    userGender: Union[str, None] = None
    userMobilePhone: Union[str, None] = None
    bikeType: Union[Bike, None] = None

class FormInDB(Form):
    submittingUser: str



app = FastAPI()
app.include_router(users.router, prefix="/users", tags=["users"])


'''
@app.post("/contracts/add/")
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







