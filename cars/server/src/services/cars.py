

from __future__ import annotations

from src.exceptions import (
    CarNotFoundException,
    DatabaseException,
    DuplicateCarException,
    EmptyPayloadException,
    InvalidIDException
)
from src.logger import get_logger
from src.schemas import CarCreate,CarUpdate

logger=get_logger(__name__)

'''HELPERS'''

def _next_id(db:list[dict])->int:
    """return max existing ID + 1, or 1 for an empty DB"""

    return max((car["id"] for car in db),default=0)+1

def _find_car(db:list[dict],car_id:int)->dict:
    """locate a car by ID or raise CarNotFoundException"""

    for car in db:
        if car["id"]==car_id:
            return car
        
    raise CarNotFoundException(
        f"Car with ID {car_id} does not exist.",
        context={"car_id":car_id}
    )

def _assert_no_duplicates(db:list[db],name:str,brand:str,exclude_id:int|None=None)->None:
    """raise DuplicateCarException if a car with the same name+brand exists"""

    for car in db:
        if exclude_id is not None and car["id"]==exclude_id:
            continue
        if car["name"]==name.lower() and car["brand"]==brand.lower():
            raise DuplicateCarException(
                f"A car named '{name}' by '{brand}' already exists (ID {car['id']}).",
                context={"existing_id":car["id"],"name":name,"brand":brand}
            )


'''CRUD OPERATIONS'''

def list_cars(
    db: list[dict],
    *,
    brand: str | None = None,
    min_price_cr: float | None = None,
    max_price_cr: float | None = None,
    limit: int = 100,
    offset: int = 0,
)->list[dict]:
    """return cars with optional filtering and pagination"""

    print(f"offset {type(offset)} {offset} | limit {type(limit)} {limit} | ")

    results=list(db)

    if results and brand:
        results=[car for car in results if car["brand"].lower==brand.lower]

    if min_price_cr is not None and max_price_cr is not None:
        filtered=[]
        for car in results:
            try:
                price=float(car["price"].replace("₹","").replace("Cr",""))
            except Exception as e:
                logger.warning(
                    "Could not parse price for car", extra={"car_id": car["id"], "price": car["price"]}
                )
                continue
            if price<min_price_cr:
                continue
            if price>max_price_cr:
                continue

            filtered.append(car)
        results=filtered

    if results and offset>=len(results):
        return []
    
    paginated=results[offset:offset+limit]

    logger.info(
        "listed cars",
        extra={
            "total_matches":results,
            "returned":paginated,
            "brand_filter": brand,
            "offset": offset,
            "limit": limit,
        }
    )
    
    return paginated


def get_car(db:list[dict],car_id:int)->dict:
    """fetch a single car by ID"""
     
    if car_id<1:
        raise InvalidIDException(f"ID must be a positive integer, got {car_id}")
    
    car=_find_car(db,car_id)
    logger.info("Fetched car", extra={"car_id": car_id})
    return car

def create_car(db:list[dict],payload:CarCreate)->dict:
    """create and persist a new car"""

    _assert_no_duplicates(db,payload.name,payload.brand)

    new_car:dict={
        "id":_next_id(db),
        "name":payload.name,
        "brand":payload.brand,
        "price":payload.price,
        "image_url":payload.image_url
    }

    try:
        db.append(new_car)

    except Exception as exc:
        #?what does the below statement do?
        raise DatabaseException(
            "Failed to persist new car.",
            context={"payload": payload.model_dump(), "error": str(exc)}
        ) from exc
    
    logger.info("Created car", extra={"car_id": new_car["id"], "name": new_car["name"]})
    return new_car


def update_car(db:list[dict],car_id:int,payload:CarUpdate)->dict:
    """partially update an existing car"""

    if car_id<1:
        raise InvalidIDException(f"ID must be a positive integer, got {car_id}")
    
    updates=payload.model_dump(exclude_none=True)
    if not updates:
        raise EmptyPayloadException("no fields to update were provided.")
    
    car=_find_car(db,car_id)
    
    new_name=updates.get(payload.name,car["name"])
    new_brand=updates.get(payload.brand,car["brand"])

    _assert_no_duplicates(db,new_name,new_brand,exclude_id=car_id)

    car.update(updates) #merges both dict's , the latter key overrides the former key if exists

    return car


def delete_car(db: list[dict], car_id: int) -> dict:
    """delete a car by ID."""
    
    if car_id < 1:
        raise InvalidIDException(f"ID must be a positive integer, got {car_id}.")

    car = _find_car(db, car_id)
    db.remove(car)
    logger.info("Deleted car", extra={"car_id": car_id, "name": car["name"]})
    return car