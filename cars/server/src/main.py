import uvicorn
import asyncio
from fastapi import FastAPI,HTTPException,Depends
from contextlib import asynccontextmanager

from src.api import router
from src.schemas import Car
from data import CAR_DB

car_db=[Car(**car) for car in CAR_DB]

@asynccontextmanager
async def cars_lifespan(app:FastAPI):  #!lifespan expects a callable with the "app" argument
    print("[MAIN] Loading Heavy Car Model")
    print("[MAIN] Loading Car DB")

    await asyncio.sleep(2)

    HEAVY_CAR_MODEL:str="LOADED"

    app.state.car_model=HEAVY_CAR_MODEL
    app.state.db=car_db

    yield None #yield X , X gets automatically attached to app.state

    print("[MAIN] Unloading Heavy Car Model")
    print("[MAIN] Unloading Car DB")

    HEAVY_CAR_MODEL:str="UNLOADED"
    del app.state.db



app=FastAPI(title="Shelby American",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
            lifespan=cars_lifespan)

app.include_router(router,prefix="/api/v1")

@app.get("/")
def screening():
    return {"success":True,"message":"Welcome to Shelby American . Get Ready to dive into the world of fast,sexy and exotic cars . Buckle Up!!"}


@app.get("/health")
def health_check():
    return {"success":True,"message":"Application running smoothly"}






if __name__=="__main__":
    uvicorn.run("src.main:app",port=7000,reload=True)
