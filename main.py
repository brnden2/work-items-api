from contextlib import asynccontextmanager
from typing import Literal
from config import FRONTEND_ORIGINS
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from database import create_db_and_tables, get_session
from models import WorkItem

from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    title="Work Items API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=FRONTEND_ORIGINS, 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"],
    )


class WorkItemCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    status: Literal["open", "in_progress", "completed"] = "open"


class WorkItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    status: Literal["open", "in_progress", "completed"] | None = None

@app.get("/")
def read_root():
    return {
        "message": "Work Items API is running"
    }


@app.post("/work-items", status_code=201)
def create_work_item(item: WorkItemCreate, session: Session = Depends(get_session)):
    db_item = WorkItem(
        title=item.title,
        status=item.status
    )

    session.add(db_item)
    session.commit()
    session.refresh(db_item)

    return db_item


@app.get("/work-items")
def get_work_items(
    session: Session = Depends(get_session)
):
    statement = select(WorkItem)
    items = session.exec(statement).all()

    return items


@app.get("/work-items/{item_id}")
def get_work_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(WorkItem, item_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Work item not found"
        )

    return item


@app.patch("/work-items/{item_id}")
def update_work_item(item_id: int, update: WorkItemUpdate, session: Session = Depends(get_session)):
    item = session.get(WorkItem, item_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Work item not found"
        )
    
    update_data = update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(item, key, value)
    
    session.add(item)
    session.commit()
    session.refresh(item)

    return item


@app.delete("/work-items/{item_id}", status_code=204)
def delete_work_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(WorkItem, item_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Work item not found"
        )
    
    session.delete(item)
    session.commit()