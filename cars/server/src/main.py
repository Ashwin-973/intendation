import uvicorn
import asyncio
from fastapi import FastAPI,HTTPException,Depends
from contexlib import asynccontextmanager

app=FastAPI(title="Shelby American",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc")

@asynccontextmanager
async def cars_lifespan():
    print("[MAIN] Loading Heavy Car Model")

    await asyncio.sleep(2)

    HEAVY_CAR_MODEL:str="LOADED"

    app.state.car_model=HEAVY_CAR_MODEL

    yield None #yield X , X gets automatically attached to app.state

    print("[MAIN] Unloading Heavy Car Model")

    HEAVY_CAR_MODEL:str="UNLOADED"


@app.get("/")
def screening():
    return {"success":True,"message":"Welcome to Shelby American . Get Ready to dive into the world of fast,sexy and exotic cars . Buckle Up!!"}


@app.get("/health")
def health_check():
    return {"success":True,"message":"Application running smoothly"}



    














if __name__=="__main__":
    uvicorn.run(app,host="127.0.0.1",port=6000,reload=True)
