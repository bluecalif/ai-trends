"""RSS collection API schemas."""
from pydantic import BaseModel


class CollectResponse(BaseModel):
    """Response for collection endpoint."""
    message: str
    source_id: int
    count: int
    
    class Config:
        from_attributes = True


class CollectAllResponse(BaseModel):
    """Response for collect all endpoint."""
    results: list[dict]
    
    class Config:
        from_attributes = True

