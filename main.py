from typing import Annotated, Union
from pydantic import BaseModel, EmailStr
from enum import Enum
from fastapi import Depends, FastAPI
from datetime import date
from typing import Annotated, Union
from pydantic import BaseModel, EmailStr
from enum import Enum
from routers import  users, contracts



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







app = FastAPI()
app.include_router(users.router, prefix="", tags=["Users"])
app.include_router(contracts.router, prefix="/contracts", tags=["Contracts"])










