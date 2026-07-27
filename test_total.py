from fuel import Fuel

f = Fuel(car="Volvo FH", liters=500, price_per_liter=1.85, mileage=150000)

print(f)
print(f'Total Price: {f.total_price()} $')