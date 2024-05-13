from pydantic import BaseModel

from typing import List, Tuple, Union


class NAW(BaseModel):
    name: str
    duckets: Union[int, str]
