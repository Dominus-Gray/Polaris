"""
Pagination and Filtering Standards for API Hardening
Implements consistent pagination, filtering, and sorting for list endpoints
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from fastapi import Query
from datetime import datetime, timedelta
import uuid

# Pagination Models
class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    page: int = Field(1, ge=1, le=1000, description="Page number (1-based)")
    limit: int = Field(20, ge=1, le=100, description="Items per page")
    
    @validator('limit')
    def validate_limit(cls, v):
        if v > 100:
            raise ValueError('Limit cannot exceed 100 items per page')
        return v
    
    @property
    def offset(self) -> int:
        """Calculate offset from page and limit"""
        return (self.page - 1) * self.limit

class PaginationInfo(BaseModel):
    """Pagination metadata for responses"""
    page: int
    limit: int
    total_count: int
    total_pages: int
    has_next: bool
    has_prev: bool
    next_page: Optional[int] = None
    prev_page: Optional[int] = None

class FilterParams(BaseModel):
    """Standard filtering parameters"""
    created_after: Optional[datetime] = Field(None, description="Filter items created after this date")
    created_before: Optional[datetime] = Field(None, description="Filter items created before this date") 
    updated_after: Optional[datetime] = Field(None, description="Filter items updated after this date")
    updated_before: Optional[datetime] = Field(None, description="Filter items updated before this date")
    status: Optional[List[str]] = Field(None, description="Filter by status values")
    search: Optional[str] = Field(None, max_length=200, description="Text search query")

class SortParams(BaseModel):
    """Standard sorting parameters"""
    sort_by: str = Field("created_at", description="Field to sort by")
    sort_order: str = Field("desc", regex="^(asc|desc)$", description="Sort order: asc or desc")

class PaginatedResponse(BaseModel):
    """Standard paginated response wrapper"""
    data: List[Any]
    pagination: PaginationInfo
    filters_applied: Dict[str, Any]
    sort_applied: Dict[str, str]

# Idempotency Support
class IdempotencyKey(BaseModel):
    """Idempotency key model"""
    key: str = Field(..., min_length=1, max_length=255, description="Client-provided idempotency key")
    
    @validator('key')
    def validate_key(cls, v):
        # Ensure key is alphanumeric with hyphens and underscores
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Idempotency key must contain only alphanumeric characters, hyphens, and underscores')
        return v

class IdempotencyRecord(BaseModel):
    """Stored idempotency record"""
    key: str
    user_id: str
    endpoint: str
    method: str
    request_hash: str
    response_body: Dict[str, Any]
    response_status: int
    created_at: datetime
    expires_at: datetime

# Helper functions for pagination
def create_pagination_info(page: int, limit: int, total_count: int) -> PaginationInfo:
    """Create pagination metadata"""
    total_pages = (total_count + limit - 1) // limit  # Ceiling division
    has_next = page < total_pages
    has_prev = page > 1
    
    return PaginationInfo(
        page=page,
        limit=limit,
        total_count=total_count,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
        next_page=page + 1 if has_next else None,
        prev_page=page - 1 if has_prev else None
    )

def build_filter_query(filters: FilterParams) -> Dict[str, Any]:
    """Build MongoDB query from filter parameters"""
    query = {}
    
    # Date range filters
    if filters.created_after or filters.created_before:
        query["created_at"] = {}
        if filters.created_after:
            query["created_at"]["$gte"] = filters.created_after
        if filters.created_before:
            query["created_at"]["$lte"] = filters.created_before
    
    if filters.updated_after or filters.updated_before:
        query["updated_at"] = {}
        if filters.updated_after:
            query["updated_at"]["$gte"] = filters.updated_after
        if filters.updated_before:
            query["updated_at"]["$lte"] = filters.updated_before
    
    # Status filter
    if filters.status:
        query["status"] = {"$in": filters.status}
    
    # Text search
    if filters.search:
        query["$text"] = {"$search": filters.search}
    
    return query

def build_sort_spec(sort: SortParams) -> List[tuple]:
    """Build MongoDB sort specification"""
    direction = 1 if sort.sort_order == "asc" else -1
    return [(sort.sort_by, direction)]

# Dependency functions for FastAPI
def get_pagination_params(
    page: int = Query(1, ge=1, le=1000, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
) -> PaginationParams:
    """Dependency for pagination parameters"""
    return PaginationParams(page=page, limit=limit)

def get_filter_params(
    created_after: Optional[datetime] = Query(None, description="Filter items created after this date"),
    created_before: Optional[datetime] = Query(None, description="Filter items created before this date"),
    updated_after: Optional[datetime] = Query(None, description="Filter items updated after this date"),
    updated_before: Optional[datetime] = Query(None, description="Filter items updated before this date"),
    status: Optional[List[str]] = Query(None, description="Filter by status values"),
    search: Optional[str] = Query(None, max_length=200, description="Text search query")
) -> FilterParams:
    """Dependency for filter parameters"""
    return FilterParams(
        created_after=created_after,
        created_before=created_before,
        updated_after=updated_after,
        updated_before=updated_before,
        status=status,
        search=search
    )

def get_sort_params(
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order")
) -> SortParams:
    """Dependency for sort parameters"""
    return SortParams(sort_by=sort_by, sort_order=sort_order)

# Idempotency utilities
import hashlib
import json

def generate_request_hash(method: str, path: str, body: Any) -> str:
    """Generate hash of request for idempotency checking"""
    content = f"{method}:{path}:{json.dumps(body, sort_keys=True, default=str)}"
    return hashlib.sha256(content.encode()).hexdigest()

async def check_idempotency(
    db, user_id: str, idempotency_key: str, 
    method: str, endpoint: str, request_body: Any
) -> Optional[IdempotencyRecord]:
    """Check if request is idempotent and return cached response if exists"""
    request_hash = generate_request_hash(method, endpoint, request_body)
    
    # Look for existing idempotency record
    record = await db.idempotency_records.find_one({
        "key": idempotency_key,
        "user_id": user_id,
        "endpoint": endpoint,
        "method": method,
        "expires_at": {"$gt": datetime.utcnow()}
    })
    
    if record:
        # Check if request hash matches (same request)
        if record["request_hash"] == request_hash:
            return IdempotencyRecord(**record)
        else:
            # Same key, different request - this is an error
            from fastapi import HTTPException
            raise HTTPException(
                status_code=422,
                detail="Idempotency key reused with different request"
            )
    
    return None

async def store_idempotency_record(
    db, user_id: str, idempotency_key: str,
    method: str, endpoint: str, request_body: Any,
    response_body: Dict[str, Any], response_status: int,
    ttl_hours: int = 24
) -> None:
    """Store idempotency record for future requests"""
    request_hash = generate_request_hash(method, endpoint, request_body)
    expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
    
    record = {
        "_id": str(uuid.uuid4()),
        "key": idempotency_key,
        "user_id": user_id,
        "endpoint": endpoint,
        "method": method,
        "request_hash": request_hash,
        "response_body": response_body,
        "response_status": response_status,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at
    }
    
    await db.idempotency_records.insert_one(record)