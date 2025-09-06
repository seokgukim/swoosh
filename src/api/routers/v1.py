from fastapi import APIRouter, Response

from ..features.auth import router as auth_router

router = APIRouter()
router.include_router(auth_router)

@router.get("/")
async def read_root():
    """
    Root endpoint for the Swoosh API.
    """
    return Response(content="Welcome to the Swoosh API!", media_type="application/json")


@router.get("/items/{item_id}")
async def read_item(item_id: int):
    """
    (Test Endpoint) Retrieve an item by its ID.
    """
    items = {1: "Item One", 2: "Item Two", 3: "Item Three"}
    if item_id not in items:
        return Response(content="Item not found", status_code=404)
    return Response(content=items[item_id], media_type="application/json")
