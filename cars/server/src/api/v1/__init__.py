
from fastapi import APIRouter

from .cars import router as cars_router

router=APIRouter()
router.include_router(cars_router)

__all__=[
    "router"
]