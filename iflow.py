from pydantic import BaseModel

from typing import List, Tuple, Union, Optional
from iflow2 import NAW


class Caw(BaseModel):
    name: str
    that: Optional[NAW]


# Example Pydantic classes
class Address(BaseModel):
    street: str
    city: str
    zip_code: str


class Person(BaseModel):
    name: str
    age: Tuple[int, int]
    address: Address
    at: Union[str, Caw, int]


class Company(BaseModel):
    name: str
    location: Address
    employees: List[Person]
    daw: Caw
