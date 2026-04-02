

from fastapi import Request

def get_db(req:Request):
    print("[DEPENEDNCIES] providing a route access to db")
    yield req.app.state.db
    print("[DEPENEDNCIES] route handler finished execution")