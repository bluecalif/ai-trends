"""Constants API endpoints.

This module provides API endpoints to expose application constants
for frontend-backend contract synchronization.
"""
from fastapi import APIRouter

from backend.app.core.constants import FIELDS, CUSTOM_TAGS

router = APIRouter(prefix="/api/constants", tags=["constants"])


@router.get("/fields")
async def get_fields():
    """Get field categories list.
    
    Returns:
        dict: Field categories list
    """
    return {"fields": FIELDS}


@router.get("/custom-tags")
async def get_custom_tags():
    """Get custom AI tags list.
    
    Returns:
        dict: Custom AI tags list
    """
    return {"tags": CUSTOM_TAGS}

