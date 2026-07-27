from sqlalchemy import create_engine, Column,Integer,String, Float
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "postgresql://postgres:postgres123@db:5432/fueltracker"
engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class FuelUpDB(Base):
    __tablename__ = "fuelups"
    
    id = Column(Integer, primary_key=True)
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