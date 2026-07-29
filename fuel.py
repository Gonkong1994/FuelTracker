from pydantic import BaseModel, Field



class FuelUp(BaseModel):
    
    id: int = Field(default=0)
    plate_number:str = Field(...,min_length=6, description="Plate number")
    car: str = Field(..., min_length = 2, description = 'Client car')
    liters: float = Field(default = 0, ge = 0, description = 'Liters refueled')
    price_per_liter: float = Field(default = 0, ge = 0, description = 'Price for one liter')
    kilometrs: int = Field(default=0, ge = 0, description = 'Kilometr')
    date: str = Field(default='', pattern=r'^\d{4}-\d{2}-\d{2}$', description='Date of refuel (YYYY-MM-DD)')
    
    def __str__(self) -> str:
        return f"FuelUp(car='{self.car}', liters={self.liters}, price={self.total_price()})"
    
    def total_price(self) -> float:
        return self.liters * self.price_per_liter
    
class FuelUpUpdate(BaseModel):
    plate_number: str | None = None
    car: str | None = None
    liters: float | None = None
    price_per_liter: float | None = None
    kilometrs: int | None = None
    date: str | None = None
        