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



from fastapi import APIRouter,HTTPException,Depends,Query
from typing import Annotated


from src.schemas import Car
from src.db import get_db



router=APIRouter()

@router.get("/cars/{id}",response_model=Car|dict[str,bool|str])
def get_car(id:int,db:list[Car]=Depends(get_db)):
    print("[ROUTER] GET /cars/id")
    retrieved_car=None
    for car_data in db: #!prevented variable shadowing
        if car_data.id==id:
            retrieved_car=car_data
            return retrieved_car 
    return {"success":False,"message":"car object with the given id does not exist"}  

@router.get("/cars",response_model=list[Car])
def get_all_cars(db:list[Car]=Depends(get_db)):
    print("[ROUTER] GET /cars")
    print(db)
    return db

@router.post("/cars",response_model=Car)
def create_car(car:Car,db:list[Car]=Depends(get_db)):
    print("[ROUTER] POST /cars")
    db.append(car)
    print(db)
    return db[len(db) - 1]  


@router.put("/cars/{id}",response_model=Car)
def update_car(id:int,car:Car,db:list[Car]=Depends(get_db)):
    print("[ROUTER] PUT /cars")

    for idx,car_data in enumerate(db):
        if car_data.id==id:
            db[idx]=car
            return db[idx]
    return {"success":False,"message":"car object with the given id does not exist"}  

@router.patch("/cars/{id}",response_model=Car)
def patch_car(id:int,name:Annotated[str|None,Query(min_length=3)]=None,brand:str|None=None,price:str|None=None,image_url:str|None=None,db:list[Car]=Depends(get_db)):
    print("[ROUTER] PATCH /cars")
    if not (name or brand or price or image_url):
        raise HTTPException(400,detail="nothing to patch. incomplete info")
    
    for idx,car_data in enumerate(db):
        if car_data.id==id:
            updated_car=Car(
                id=car_data.id,
                name=name or car_data.name,
                brand=brand or car_data.brand,
                price=price or car_data.price,
                image_url=image_url or car_data.image_url,
            )
            db[idx]=updated_car
            return db[idx]

    return {"success":False,"message":"car object with the given id does not exist"}  


@router.delete("/cars/{id}",response_model=dict[str,bool|str])
def delete_car(id:int,db:list[Car]=Depends(get_db)):
    print("[ROUTER] DELETE /cars")
    
    for idx,car_data in enumerate(db):
        if car_data.id==id:
            del db[idx]
            return {"success":True,"message":"car has been deleted"}  
    return {"success":False,"message":"car object with the given id does not exist"}  
    

    
    

