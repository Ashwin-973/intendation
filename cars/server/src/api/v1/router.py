'''from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
from ..dependencies import get_db
from ...db.models.car_model import Car

router = APIRouter()

# Create a new car
@router.post("/cars", response_model=Car)
def create_car(car: Car, db: Dict[int, Car] = Depends(get_db)):
    if car.id in db:
        raise HTTPException(status_code=400, detail="Car with this ID already exists.")
    db[car.id] = car
    return car

# Read all cars
@router.get("/cars", response_model=list[Car])
def get_all_cars(db: Dict[int, Car] = Depends(get_db)):
    return list(db.values())

# Read a car by ID
@router.get("/cars/{car_id}", response_model=Car)
def get_car(car_id: int, db: Dict[int, Car] = Depends(get_db)):
    if car_id not in db:
        raise HTTPException(status_code=404, detail="Car not found.")
    return db[car_id]

# Update a car
@router.put("/cars/{car_id}", response_model=Car)
def update_car(car_id: int, updated_car: Car, db: Dict[int, Car] = Depends(get_db)):
    if car_id not in db:
        raise HTTPException(status_code=404, detail="Car not found.")
    db[car_id] = updated_car
    return updated_car

# Delete a car
@router.delete("/cars/{car_id}", response_model=dict)
def delete_car(car_id: int, db: Dict[int, Car] = Depends(get_db)):
    if car_id not in db:
        raise HTTPException(status_code=404, detail="Car not found.")
    del db[car_id]
    return {"success": True, "message": "Car deleted successfully."}'''



from fastapi import APIRouter,HTTPException,Depends


from src.schemas import Car
from src.db import get_db



router=APIRouter()

@router.get("/cars/{id}",response_model=list[Car])
def get_car(id:int,db:list[dict]=Depends(get_db)):
    print("[ROUTER] GET /cars/id")
    return db[id]
