from storage import Session, FuelUpDB, load_fuelups
from fuel import FuelUp, FuelUpUpdate
from fastapi import FastAPI, Body, UploadFile, File
from datetime import date
from fastapi.responses import StreamingResponse
import csv
import io

app = FastAPI(title="FuelTracker")

def db_to_pydantic(db_fuelup):
    if db_fuelup is None:
        return None
    return FuelUp(
        id=db_fuelup.id,
        plate_number = db_fuelup.plate_number,
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
    
@app.get("/fuelups/today")
def get_today():
    today = str(date.today())
    session = Session()
    db_fuelup = session.query(FuelUpDB).filter(FuelUpDB.date == today).all()
    session.close()
    return [db_to_pydantic(f).model_dump() for f in db_fuelup]

@app.get("/fuelups/month")
def get_month(year: int, month: int):
    prefix = f"{year}-{month:02d}"
    session = Session()
    all_fuelups = session.query(FuelUpDB).all()
    session.close()
    result = [f for f in all_fuelups if f.date.startswith(prefix)]
    return [db_to_pydantic(f).model_dump() for f in result]
    
@app.get("/fuelups/summary")
def get_summary():
    session = Session()
    all_fuelups = session.query(FuelUpDB).all()
    session.close()
    
    summary = {}
    for f in all_fuelups:
        plate = f.plate_number
        if plate not in summary:
            summary[plate] = {"total_liters": 0, "total_spent": 0}
        summary[plate]["total_liters"] += f.liters
        summary[plate]["total_spent"] += f.liters * f.price_per_liter
    for plate in summary:
        summary[plate]["total_spent"] = round(summary[plate]["total_spent"], 2)
    return summary

@app.get("/fuelups/export")
def export_csv():
    session = Session()
    all_fuelups = session.query(FuelUpDB).all()
    session.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "plate_number", "car", "liters", "price_per_liter", "kilometers", "date"])
    for f in all_fuelups:
        writer.writerow([f.id, f.plate_number, f.car, f.liters, f.price_per_liter, f.kilometrs, f.date])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=fuelups.csv"}
    )
    
@app.get("/fuelups/import")
def import_csv(file: UploadFile = File(...)):
    content = file.file.read().decode("utf-8")
    reader = csv.reader(io.StringIO(content))
    session = Session()
    count = 0
    
    next(reader, None)
    for row in reader:
        if len(row) >= 6:
            db_fuelup = FuelUpDB(
                plate_number=row[0],
                car=row[1],
                liters=float(row[2]),
                price_per_liter=float(row[3]),
                kilometrs=int(row[4]),
                date=row[5]
            )
            session.add(db_fuelup)
            count += 1
    session.commit()
    session.close()
    return {"imported": count}


@app.get("/fuelups/{id}")
def get_fuelup(id:int):
    session = Session()
    db_fuelup = session.query(FuelUpDB).filter(FuelUpDB.id == id).first()
    session.close()
    if db_fuelup:
        return db_to_pydantic(db_fuelup).model_dump()
    return {"Error":"Fuelup not found"}

@app.post("/fuelups/")
def create_fuelup(plate_number: str = Body(...), car: str = Body(...), liters: float = Body(...), price_per_liter: float = Body(...), kilometrs: int = Body(...), date: str = Body(...)):
    session = Session()
    db_fuelup = FuelUpDB(plate_number = plate_number, car = car, liters = liters, price_per_liter = price_per_liter, kilometrs =kilometrs, date =date)
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
def edit_fuelup(id:int, data : FuelUpUpdate = Body(...)):
    session = Session()
    db_fuelup = session.query(FuelUpDB).filter(FuelUpDB.id == id).first()
    if db_fuelup:
        if data.plate_number is not None:
            db_fuelup.plate_number = data.plate_number
        if data.car is not None:
            db_fuelup.car = data.car
        if data.liters is not None:
            db_fuelup.liters = data.liters
        if data.price_per_liter is not None:
            db_fuelup.price_per_liter = data.price_per_liter
        if data.kilometrs is not None:
            db_fuelup.kilometrs = data.kilometrs
        if data.date is not None:
            db_fuelup.date = data.date
        session.commit()
        result = db_to_pydantic(db_fuelup).model_dump()
        session.close()
        return result
    session.close()
    return {"error":"FuelUp not found"}

@app.get("/fuelups/plate/{plate_number}")
def get_by_plate(plate_number:str):
    session = Session()
    db_fuelup = session.query(FuelUpDB).filter(FuelUpDB.plate_number == plate_number).all()
    session.close()
    return [db_to_pydantic(f).model_dump() for f in db_fuelup]

@app.get("/fuelups/plate/{plate_number}/stats")
def get_plate_stats(plate_number: str):
    session = Session()
    db_fuelup = session.query(FuelUpDB).filter(FuelUpDB.plate_number == plate_number).all()
    session.close()
    
    total_liters = sum(f.liters for f in db_fuelup)
    total_spent = sum(f.liters * f.price_per_liter for f in db_fuelup)
    
    return {
        "Plate number" : plate_number,
        "Total_fuelups" : len(db_fuelup),
        "Total liters" : total_liters,
        "Total spent" : round(total_spent, 2)
    } 

