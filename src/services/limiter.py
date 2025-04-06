from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import APIRouter, Request
from src.schemas.users import User

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=User,
    description="No more than 10 requests per minute"
)
@limiter.limit("5/minute")
async def my_endpoint(request: Request):
    """
    Protected route with rate limiting.

    :param request: FastAPI request object.
    :return: Message confirming successful access.
    """
    return {"message": "This is my rate-limited endpoint."}
