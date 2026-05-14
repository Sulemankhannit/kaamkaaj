from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, date

if TYPE_CHECKING:
    from schemas.khiladi import Khiladi

class DailyMessage(SQLModel, table=True):
    __tablename__ = "daily_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    khiladi_id: int = Field(foreign_key="khiladi.id", index=True)
    message: str
    message_type: str
    mood: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    shown_at: date = Field(default_factory=date.today)
    was_interacted: bool = Field(default=False)
    message_hash: Optional[str] = Field(default=None)

class DailyMessageResponse(SQLModel):
    message: str
    message_type: str
    mood: str
    is_new: bool
    refresh_available_at: datetime
