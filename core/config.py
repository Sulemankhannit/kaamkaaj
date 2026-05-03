import os
from dotenv import load_dotenv
from sqlmodel import create_engine,Session
import urllib.parse
load_dotenv()

SECRET_KEY=os.getenv("KAAMKAJ_SECRET_KEY");
print(SECRET_KEY)

db_user=os.getenv("DB_USER")
db_password=os.getenv("DB_PASSWORD")
db_host=os.getenv("HOST")
db_port=os.getenv("PORT")
db_name=os.getenv("DB_NAME")
smtp_email=os.getenv("SMTP_EMAIL")
smtp_password=os.getenv("SMTP_PASSWORD")

safe_pw=urllib.parse.quote_plus(db_password)
postgres_url=f"postgresql://{db_user}:{safe_pw}@{db_host}:{db_port}/{db_name}"


engine=create_engine(postgres_url,echo=True)

def get_session():
    with Session(engine) as session:
        yield session


