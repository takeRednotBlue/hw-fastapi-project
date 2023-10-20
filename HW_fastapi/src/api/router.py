from fastapi import APIRouter
from src.api.contacts import router as contacts_router
from src.api.auth import router as auth_router

router = APIRouter(prefix='/v1')

router.include_router(contacts_router)
router.include_router(auth_router)
