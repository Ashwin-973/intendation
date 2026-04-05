
from fastapi import APIRouter,Depends,Query,status
from typing import Annotated


from cars.server.src.logger import get_logger
from src.schemas import CarResponse,CarCreate,CarUpdate
from src.db import get_db
from cars.server.src.services import cars1 as car_collection



logger=get_logger(__name__)
router=APIRouter(prefix="/cars",tags=["cars"])

DB=Annotated[list[dict],Depends(get_db)]


'''GET ALL'''

@router.get(
    "",
    response_model=list[CarResponse],
    summary="List all cars",
    description=(
        "Returns a paginated list of cars. "
        "Supports optional filtering by brand, and price range in Crores."
    ))
def get_cars(
    db:DB,
    brand:Annotated[str|None,Query(description="Filter by brand name (case-insensitive)")]=None,
    min_price:Annotated[float|None,Query(ge=0,description="Min price in Crores (e.g. 1.5)")]=None,
    max_price:Annotated[float|None,Query(ge=0, description="Max price in Crores (e.g. 10.0)")]=None,
    limit:Annotated[int,Query(ge=1, le=100, description="Max results to return")]=20,
    offset:Annotated[int,Query(ge=0,description="Records to skip")]=0
)->list[dict]:
    return car_collection.list_cars(
        db=db,
        brand=brand,
        min_price_cr=min_price,
        max_price_cr=max_price,
        limit=limit,
        offset=offset
    )


'''GET'''

@router.get(
    "/{car_id}",
    response_model=CarResponse,
    summary="Get a single car",
    responses={
        404:{"detail":"Car not found"},
        429:{"detail":"Invalid car_id (not a positive integer)"}
    })
def get_car(car_id:int,db:DB)->dict:
    return car_collection.get_car(car_id=car_id,db=db)



'''POST'''

@router.post(
    "",
    response_model=CarResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new car",
    responses={
        409:{"detail":"Car with same name + brand already exists"},
        422:{"detail":"Validation error in request body"}
    }
)
def create_car(car_payload:CarCreate,db:DB)->dict:
    return car_collection.create_car(payload=car_payload,db=db)


'''PUT'''

@router.put(
    "/{car_id}",
    response_model=CarResponse,
    summary="Update an existing car",
    responses={
        400: {"description": "Empty payload or business validation failure"},
        404: {"description": "Car not found"},
        409: {"description": "Conflict with existing car"},
        422: {"description": "Schema validation error"},
    }
)
def update_car(car_id:int,db:DB,car_payload:CarUpdate)->dict:
    return car_collection.update_car(car_id=car_id,car_payload=car_payload,db=db)


'''PATCH'''

#TODO : add a PATCH endpoint with a responses model


'''DELETE'''

@router.delete(
    "/{car_id}",
    response_model=CarResponse,
    summary="Delete a car",
    responses={
        404: {"description": "Car not found"},
    }
)
def delete_car(car_id:int,db:DB)->dict:
    return car_collection.delete_car(car_id=car_id,db=db)