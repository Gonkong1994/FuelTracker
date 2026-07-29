import os
os.environ["POSTGRES_HOST"] = "localhost"

from starlette.testclient import TestClient
from app import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "FuelTracker API is running!"}
    
def test_create_fuelup():
    response = client.post("/fuelups/", json={
        "car": "Volvo FH",
        "liters": 500,
        "price_per_liter": 1.85,
        "kilometrs": 150000,
        "date": "2026-07-28"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["car"] == "Volvo FH"
    assert data["liters"] == 500
    
def test_get_fueluo_not_found():
    response = client.get("/fuelups/999999")
    assert response.status_code == 200
    assert "Error" in response.json()
    
def test_update_fuelup():
    response = client.post("/fuelups/", json={
            "car": "Volvo FH",
            "liters": 500,
            "price_per_liter": 1.85,
            "kilometrs": 150000,
            "date": "2026-07-28"
        })
    data = response.json()
    fuelup_id = data["id"]
    
    response = client.put(f"/fuelups/{fuelup_id}", json={
        "car": "Scania Updated",
        "liters": 350
    })
    
    assert response.status_code == 200
    updated = response.json()
    assert updated["car"] == "Scania Updated"
    assert updated["liters"] == 350
    
def test_delete_fuelup():
    response = client.post("/fuelups/", json={
        "car": "Mercedes",
        "liters": 300,
        "price_per_liter": 1.45,
        "kilometrs": 155000,
        "date": "2026-07-29"
        })
    data = response.json()
    fuelup_id = data["id"]
     
    response = client.delete(f"/fuelups/{fuelup_id}")
    assert response.status_code == 200
    assert response.json() == {"deleted":fuelup_id}
     
     
    
    
    