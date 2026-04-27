import os
from dotenv import load_dotenv
from sqlmodel import create_engine,Session
load_dotenv()
SECRET_KEY=os.getenv("KAAMKAJ_SECRET_KEY");
print(SECRET_KEY)

sqllite_file_name="kaamkaaj.db"
sqlite_url=f"sqlite:///{sqllite_file_name}"
connect_args={"check_same_thread":False}
engine=create_engine(sqlite_url,connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session


