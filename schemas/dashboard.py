from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 1. The Deepest Layer: The Task
class DashboardKaamResponse(BaseModel):
    id: int
    title: str
    description:str|None
    status: str
    xp_reward: int
    requires_verification: bool
    deadline:datetime|None=None

# 2. The Middle Layer: The Goal (Contains a list of Tasks)
class DashboardLakshyaResponse(BaseModel):
    id: int
    title: str
    description: str|None=None
    is_accomplished: bool
    deadline:datetime|None=None
    kaams: List[DashboardKaamResponse] = []  # Notice the nested list!

# 3. The Top Layer: The Khiladi (Contains a list of Goals)
class DashboardResponse(BaseModel):
    khiladi_id: int
    name: str
    level: int
    current_xp: int
    lakshyas: List[DashboardLakshyaResponse] = [] 