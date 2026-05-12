from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DashboardKaamResponse(BaseModel):
    id: int
    title: str
    description:str|None
    status: str
    xp_reward: int
    requires_verification: bool
    deadline:datetime|None=None

class DashboardLakshyaResponse(BaseModel):
    id: int
    title: str
    description: str|None=None
    is_accomplished: bool
    deadline:datetime|None=None
    kaams: List[DashboardKaamResponse] = []

class DashboardResponse(BaseModel):
    khiladi_id: int
    name: str
    level: int
    current_xp: int
    xp_debt: int = 0
    in_shadow_realm: bool = False
    shadow_realm_message: str | None = None
    net_xp: int = 0
    xp_to_next_level: int = 1000
    lakshyas: List[DashboardLakshyaResponse] = [] 