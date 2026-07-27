from fastapi import FastAPI
from storage import Session, FuelUpDB, load_fuelups
from fuel import FuelUp

app = FastAPI(title="FuelTracker")

def db_to_pydantic(db_fuelup):
    if db_fuelup is None:
        return None
    return FuelUp(
        car = db_fuelup.car,
        liters = db_fuelup.liters,
        price_per_liter = db_fuelup.price_per_liter,
        kilometrs = db_fuelup.kilometrs,
        date = db_fuelup.date or ""
    )
    
    
@app.get("/")
def root():
    return {"message":"FuelTracker API is running!"}

@app.get("/fuelups")
def get_fuelups():
    fuelups = load_fuelups()
    return [db_to_pydantic(f).model_dump() for f in fuelups]

@app.get("/fuelups/stats")
def get_stats():
    session = Session()
    db_fuelup = session.query(FuelUpDB).all()
    session.close()
    total_liters = sum(f.liters for f in db_fuelup)
    total_spent = sum(f.liters *f.price_per_liter for f in db_fuelup)
    return{
        "total_fuelups": len(db_fuelup),
         "total_liters": total_liters,
         "total_spent": round(total_spent, 2)
    }

@app.get("/fuelups/{id}")
def get_fuelup(id:int):
    session = Session()
    db_fuelup = session.query(FuelUpDB).filter(FuelUpDB.id == id).first()
    session.close()
    if db_fuelup:
        return db_to_pydantic(db_fuelup).model_dump()
    return {"Error":"Fuelup not found"}

@app.post("/fuelups/")
def create_fuelup(car: str, liters: float, price_per_liter: float, kilometrs: int, date: str):
    session = Session()
    db_fuelup = FuelUpDB(car = car, liters = liters, price_per_liter = price_per_liter, kilometrs =kilometrs, date =date)
    session.add(db_fuelup)
    session.commit()
    result = db_to_pydantic(db_fuelup).model_dump()
    session.close()
    return result

@app.delete("/fuelups/{id}")
def remove_fuelup(id:int):
    session = Session()
    db_fuelup = session.query(FuelUpDB).filter(FuelUpDB.id == id).first()
    if db_fuelup:
        session.delete(db_fuelup)
        session.commit()
        session.close()
        return {"deleted":id}
    return {"Error":"Fuelup not found"}

@app.put("/fuelups/{id}")
def edit_fuelup(id:int, car:str = None, liters:float = None, price_per_liter:float = None, kilometrs:int = None):
    session = Session()
    db_fuelup = session.query(FuelUpDB).filter(FuelUpDB.id == id).first()
    if db_fuelup:
        if car is not None:
            db_fuelup.car = car
        if liters is not None:
            db_fuelup.liters = liters
        if price_per_liter is not None:
            db_fuelup.price_per_liter = price_per_liter
        if kilometrs is not None:
            db_fuelup.kilometrs = kilometrs
        session.commit()
        result = db_to_pydantic(db_fuelup).model_dump()
        session.close()
        return result
    session.close()
    return {"error":"FuelUp not found"}

