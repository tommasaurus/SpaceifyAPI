# app/api/endpoints/lease.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app import schemas, crud
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.document_processor import extract_text_from_file
from app.services.openai.openai_document import OpenAIService
from app.services.mapping_functions import parse_json, map_lease_data
from app.services.lease_processor import process_lease_upload
from io import BytesIO
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload", response_model=schemas.Lease)
async def upload_lease(
    property_id: Optional[int] = Form(None),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a lease document, process it, and create a lease.
    """    

    # Only verify property if property_id is provided
    if property_id is not None:
        property = await crud.crud_property.get_property_by_owner(
            db=db,
            property_id=property_id,
            owner_id=current_user.id
        )
        if not property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found or you do not have access to this property."
            )

    # Read the file content
    file_content = await file.read()
    
    try:
        lease = await process_lease_upload(
            file_content=file_content,
            filename=file.filename,
            property_id=property_id,  # Can be None
            document_type=document_type,
            db=db,
            owner_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the exception for debugging
        logger.exception("Unexpected error during lease processing.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )

    return lease

@router.post("/", response_model=schemas.Lease)
async def create_lease(
    lease_in: schemas.LeaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a lease by providing lease data directly.
    """
    # Ensure the property belongs to the current user
    property = await crud.crud_property.get_property(db=db, property_id=lease_in.property_id)
    if not property or property.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this property.")
    try:
        lease = await crud.crud_lease.create_lease(db=db, lease_in=lease_in, owner_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return lease

@router.get("/", response_model=List[schemas.Lease])
async def read_leases(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve leases belonging to the current user.
    """
    leases = await crud.crud_lease.get_leases(db=db, owner_id=current_user.id, skip=skip, limit=limit)
    return leases

@router.get("/{lease_id}", response_model=schemas.Lease)
async def read_lease(
    lease_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific lease by ID.
    """
    lease = await crud.crud_lease.get_lease(db=db, lease_id=lease_id, owner_id=current_user.id)
    if lease is None:
        raise HTTPException(status_code=404, detail="Lease not found")
    return lease

@router.put("/{lease_id}", response_model=schemas.Lease)
async def update_lease(
    lease_id: int,
    lease_in: schemas.LeaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a lease.
    """
    lease = await crud.crud_lease.get_lease(db=db, lease_id=lease_id, owner_id=current_user.id)
    if lease is None:
        raise HTTPException(status_code=404, detail="Lease not found")
    try:
        updated_lease = await crud.crud_lease.update_lease(db=db, lease=lease, lease_in=lease_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return updated_lease

@router.delete("/{lease_id}", response_model=schemas.Lease)
async def delete_lease(
    lease_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a lease.
    """
    try:
        lease = await crud.crud_lease.delete_lease(db=db, lease_id=lease_id, owner_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return lease
