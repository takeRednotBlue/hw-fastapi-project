from typing import Annotated

from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserDb

router = APIRouter(prefix='/users', tags=["users"])

current_user = Annotated[User, Depends(auth_service.get_current_user)]
connect_db = Annotated[Session, Depends(get_db)]


@router.get("/me", response_model=UserDb)
async def read_users_me(file: UploadFile = File(), current_user: current_user, 
                        db: connect_db):
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secret=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f"Contacts/{current_user.username}", overwrite=True)
    src_url = cloudinary.CloudinaryImage(f"Contacts/{current_user.username}")\
                        .build_url(width=250, height=250, crop="fill", vesion=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)