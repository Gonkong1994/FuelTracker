from sqlalchemy import create_engine, Column,Integer,String, Float
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'db')
DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class FuelUpDB(Base):
    __tablename__ = "fuelups"
    
    id = Column(Integer, primary_key=True)
    plate_number = Column(String(15), nullable=False)
    car = Column(String(50), nullable=False)
    liters = Column(Float, default=0)
    price_per_liter = Column(Float, default=0)
    kilometrs = Column(Integer, default=0)
    date = Column(String(20))
    
Base.metadata.create_all(engine)


def load_fuelups():
    session = Session()
    fuelup = session.query(FuelUpDB).all()
    session.close()
    return fuelup