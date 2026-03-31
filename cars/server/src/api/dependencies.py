'''from typing import Dict
from ..models.car_model import Car

# Dependency to provide the in-memory database
def get_db():
    db: Dict[int, Car] = {}
    return db'''

from ...data import CAR_DB

def get_db():
    print("[DEPENEDNCIES] providing a route access to db")
    yield CAR_DB
    print("[DEPENEDNCIES] route handler finished execution")
