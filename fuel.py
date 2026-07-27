from pydantic import BaseModel, Field

class FuelUp(BaseModel):
    
    car: str = Field(..., min_length = 2, description = 'Client car')
    liters: float = Field(default = 0, ge = 0, description = 'Liters refueled')
    price_per_liter: float = Field(default = 0, ge = 0, description = 'Price for one liter')
    kilometrs: int = Field(default=0, ge = 0, description = 'Kilometr')
    date: str = Field(default='', description = 'Date of refuel')
    
    def __str__(self) -> str:
        return f"FuelUp(car='{self.car}', liters={self.liters}, price={self.total_price()})"
    
    def total_price(self) -> float:
        return self.liters * self.price_per_liter
        