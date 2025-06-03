from pydantic import BaseModel
from enum import IntEnum
from typing import Optional

class StatusEnum(IntEnum):
    INIT = 0
    CRAWLED = 1
    GENERATED = 2
    SENT = 3
    FAILED = 4
    COMPLETED = 5

class Token(BaseModel):
    token: str

class Location(BaseModel):
    lat: float
    lng: float

class MapFactory(BaseModel):
    name: str
    address: str
    location: Location
    with_solar_panel: int = -1

class LinkedinFactory(BaseModel):
    id: str
    query: str
    companyName: Optional[str] = None
    companyID: Optional[str] = None
    companyUrl: Optional[str] = None
    description: Optional[str] = None
    fullName: Optional[str] = None
    jobTitle: Optional[str] = None
    profileUrl: Optional[str] = None
    role: Optional[str] = None
    outreachMessage: Optional[str] = None
    status: StatusEnum # 0: init, 1: crawled, 2: Generated, 3: Sent, 4: Failed, 5: Completed
