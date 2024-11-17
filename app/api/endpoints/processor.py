# app/api/endpoints/processor.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.document_processor import extract_text_from_file
from app.services.contract_processor import process_contract_upload
from app.services.invoice_processor import process_invoice_upload
from app.services.lease_processor import process_lease_upload
from app.services.openai.openai_document import OpenAIService
from io import BytesIO
import logging
from app.utils.timing import log_timing

logger = logging.getLogger(__name__)
router = APIRouter()
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a document, determine its type, and return the type to the user for confirmation.
    """
    # Read the file content
    file_content = await file.read()
    filename = file.filename
    # Extract text from the file
    file_like = BytesIO(file_content)
    text = extract_text_from_file(file_like, filename)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from the document."
        )
    # Initialize OpenAIService
    openai_service = OpenAIService()
    document_type = None
    document_type = await openai_service.determine_document_type(text)
    if not document_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not determine document type."
        )
    return document_type

@router.post("/process")
@log_timing("Total Document Processing")
async def process_document(
    property_id: int = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process the document based on the confirmed document type.
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
        if document_type.lower() == 'lease':
            # Process lease
            lease = await process_lease_upload(
                file_content=file_content,
                filename=file.filename,
                property_id=property_id,
                document_type=document_type,
                db=db,
                owner_id=current_user.id
            )
            data = lease
        elif document_type.lower() == 'invoice':
            # Process invoice
            invoice = await process_invoice_upload(
                file_content=file_content,
                filename=file.filename,
                property_id=property_id,
                document_type=document_type,
                db=db,
                owner_id=current_user.id
            )
            data = invoice
        elif document_type.lower() == 'contract':
            # Process contract
            contract = await process_contract_upload(
                file_content=file_content,
                filename=file.filename,
                property_id=property_id,
                document_type=document_type,
                db=db,
                owner_id=current_user.id
            )
            data = contract
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported document type: {document_type}"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the exception for debugging
        logger.exception(f"Unexpected error during {document_type} processing.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )
    return data