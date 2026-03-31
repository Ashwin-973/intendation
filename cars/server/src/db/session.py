
from data import CAR_DB

def get_db():
    print("[DEPENEDNCIES] providing a route access to db")
    yield CAR_DB
    print("[DEPENEDNCIES] route handler finished execution")