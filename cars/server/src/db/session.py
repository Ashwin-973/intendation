
from data import CAR_DB
from src.schemas import Car

db=[Car(**car) for car in CAR_DB]

def get_db():
    print("[DEPENEDNCIES] providing a route access to db")
    yield db
    print("[DEPENEDNCIES] route handler finished execution")