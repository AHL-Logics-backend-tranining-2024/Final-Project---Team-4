from datetime import datetime
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException

from app.api.routes.login import get_current_user
from app.models import CreateUserRequest, CreateUserResponse, UserdetailsResponse

router = APIRouter()
