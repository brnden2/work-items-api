from typing import Optional

from sqlmodel import Field, SQLModel

class WorkItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    status: str = "open"