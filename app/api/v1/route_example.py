from fastapi import APIRouter
from app.schemas.example_schema import ExampleResponse
from app.services.example_service import get_example_data

router = APIRouter()

@router.get("/example", response_model=ExampleResponse)
async def read_example():
    data = get_example_data()
    return data
