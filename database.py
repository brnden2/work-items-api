from sqlmodel import SQLModel, Session, create_engine

DATABASE_FILE = "work_items.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

connect_args = {
    "check_same_thread": False
}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session