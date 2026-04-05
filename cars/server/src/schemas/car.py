'''
Schemas for :
- car req/res
- error envelope
- health check
'''

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel,Field,field_validator,model_validator

'''HELPERS'''

_PRICE_RE=re.compile(r"^₹\d{1,6}(\.\d{1,2})?\s?Cr$")

def _validate_price(v:str)->str:
    v=v.strip()
    if not _PRICE_RE.match(v):
        raise ValueError(
            "Price must match the pattern '₹X.XX Cr' (e.g. '₹10.37 Cr') "
            f"Got . {v!r}"
        )
    return v

def _validate_name(v:str)->str:
    v=v.strip()
    if len(v)<2:
        raise ValueError("Name must be at least 2 characters long")
    if len(v)>100:
        raise ValueError("Name must be at most 100 characters long")
    
    return v

def _validate_brand(v: str) -> str:
    v = v.strip()
    if len(v) < 2:
        raise ValueError("Brand must be at least 2 characters long.")
    if len(v) > 60:
        raise ValueError("Brand must be at most 60 characters long.")
    return v


'''CAR SCHEMAS'''

class CarBase(BaseModel):
    name:str=Field(...,min_length=2,max_length=100,examples=["SF90 XX Stradale"])
    brand:str=Field(...,min_length=2,max_length=60,examples=["Ferrari"])
    price:str=Field(...,examples=[""])
    image_url:str|None=Field(default=None,max_length=2048,examples=["https://cdn.ferrari.com/..."])

    @field_validator("name")
    @classmethod
    def clean_name(cls,v:str)->str:
        return _validate_name(v)
    
    @field_validator("brand")
    @classmethod
    def clean_brand(cls,v:str)->str:
        return _validate_brand(v)
    
    @field_validator("price")
    @classmethod
    def clean_price(cls,v:str)->str:
        return _validate_price(v)
        
    @field_validator("image_url")
    @classmethod
    def clean_image_url(cls,v:str|None)->str|None:
        if v is None:
            return v
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("image_url must be a valid HTTP/HTTPS URL")
        
        return v
    
class CarCreate(CarBase):
    '''schema for POST /cars'''
    pass

class CarUpdate(BaseModel):
    '''
    schema for PUT /cars/{id}.

    all fields are optional - send only what you want to change.
    at least one field must be present (enforced in the service layer,
    not here, so that Pydantic gives you field-level errors first)'''

    name: str | None = Field(default=None, min_length=2, max_length=100)
    brand: str | None = Field(default=None, min_length=2, max_length=60)
    price: str | None = Field(default=None)
    image_url: str | None = Field(default=None, max_length=2048)

    @field_validator("name") #*runs custom validation on a field after pydantic's built in validation
    @classmethod #*all pydantic validators must be class methods and not instance methods 
    def clean_name(cls, v: str | None) -> str | None:
        return _validate_name(v) if v is not None else v

    @field_validator("brand")
    @classmethod
    def clean_brand(cls, v: str | None) -> str | None:
        return _validate_brand(v) if v is not None else v

    @field_validator("price")
    @classmethod
    def clean_price(cls, v: str | None) -> str | None:
        return _validate_price(v) if v is not None else v

    @field_validator("image_url")
    @classmethod
    def clean_image_url(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("image_url must be a valid HTTP/HTTPS URL.")
        return v
    
    @model_validator(mode="after") #*validate the entire pydantic object
    def at_least_one_field(self)->CarUpdate:
        if all(
            getattr(self,f) is None for f in ("name", "brand", "price", "image_url")
        ):
            raise ValueError("At least one field (name, brand, price, image_url) must be provided")
        
        return self
    
class CarResponse(CarBase):

    id:int

    model_config={"from attributes":True} #! ORM object support,wtf does that mean?



'''ERROR ENVELOPE'''

class ErrorDetail(BaseModel):
    '''Represents a single validation error on a specific field'''

    field:str|None=None
    message:str

class ErrorResponse(BaseModel):
    '''
    Uniform error body returned for every non-2xx response.

    Example:
    {
        "error": true,
        "error_code": "CAR_NOT_FOUND",
        "message": "No car with that ID exists.",
        "detail": null,
        "path": "/api/v1/cars/999",
        "status_code": 404
    }
    '''

    error:bool=True
    error_code:str
    message:str
    detail:Any|None=None
    path:str
    status_code:int


'''HEALTH CHECK'''

class ComponentHealth(BaseModel):
    status:str
    message:str

class HealthResponse(BaseModel):
    status:str
    version:str
    components:dict[str,ComponentHealth]