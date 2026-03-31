from pydantic import BaseModel

class Car(BaseModel):
    id:int
    name:str
    brand:str
    price:str
    image_url:str

