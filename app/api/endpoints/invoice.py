# app/api/endpoints/invoice.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import schemas, crud
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.invoice_processor import process_invoice_upload
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload", response_model=schemas.Invoice)
async def upload_invoice(
    property_id: int = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload an invoice document, process it, and create an invoice.
    """

    # Verify that the property exists and belongs to the owner
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
        invoice = await process_invoice_upload(
            file_content=file_content,
            filename=file.filename,
            property_id=property_id,
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
        logger.exception("Unexpected error during invoice processing.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )

    return invoice

@router.post("/", response_model=schemas.Invoice)
async def create_invoice(
    invoice_in: schemas.InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create an invoice by providing invoice data directly.
    """
    # Ensure the property belongs to the current user
    property = await crud.crud_property.get_property(db=db, property_id=invoice_in.property_id)
    if not property or property.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this property.")
    try:
        invoice = await crud.crud_invoice.create_invoice(db=db, invoice_in=invoice_in, owner_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return invoice

@router.get("/", response_model=List[schemas.Invoice])
async def read_invoices(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve invoices belonging to the current user.
    """
    invoices = await crud.crud_invoice.get_invoices(db=db, owner_id=current_user.id, skip=skip, limit=limit)
    return invoices

@router.get("/{invoice_id}", response_model=schemas.Invoice)
async def read_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific invoice by ID.
    """
    invoice = await crud.crud_invoice.get_invoice(db=db, invoice_id=invoice_id, owner_id=current_user.id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.put("/{invoice_id}", response_model=schemas.Invoice)
async def update_invoice(
    invoice_id: int,
    invoice_in: schemas.InvoiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an invoice.
    """
    invoice = await crud.crud_invoice.get_invoice(db=db, invoice_id=invoice_id, owner_id=current_user.id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    try:
        updated_invoice = await crud.crud_invoice.update_invoice(db=db, invoice=invoice, invoice_in=invoice_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return updated_invoice

@router.delete("/{invoice_id}", response_model=schemas.Invoice)
async def delete_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an invoice.
    """
    try:
        invoice = await crud.crud_invoice.delete_invoice(db=db, invoice_id=invoice_id, owner_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return invoice
