import os
from dotenv import load_dotenv
from sqlmodel import create_engine,Session
import urllib.parse
import cloudinary
import cloudinary.uploader
load_dotenv()

SECRET_KEY=os.getenv("KAAMKAJ_SECRET_KEY");
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True # Forces SSL encryption
)


# db_user=os.getenv("DB_USER")
# db_password=os.getenv("DB_PASSWORD")
# db_host=os.getenv("HOST")
# db_port=os.getenv("PORT")
# db_name=os.getenv("DB_NAME")
smtp_email=os.getenv("SMTP_EMAIL")
smtp_password=os.getenv("SMTP_PASSWORD")

# safe_pw=urllib.parse.quote_plus(db_password)  my local learning code
# postgres_url=f"postgresql://{db_user}:{safe_pw}@{db_host}:{db_port}/{db_name}"


postgres_url = os.getenv("DATABASE_URL") # cloud database



if postgres_url and postgres_url.startswith("postgres://"):
    postgres_url = postgres_url.replace("postgres://", "postgresql://", 1)

#engine=create_engine(postgres_url,echo=False)
engine = create_engine(
    postgres_url, 
    echo=False, 
    pool_pre_ping=True,  #  Checks if connection is alive before using it
    pool_recycle=300     #  Proactively recycles connections every 5 minutes
)

def get_session():
    with Session(engine) as session:
        yield session


