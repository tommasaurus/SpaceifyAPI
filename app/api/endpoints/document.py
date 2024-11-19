# app/api/endpoints/document.py

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    status,
    BackgroundTasks
)
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app import schemas, crud
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
import os
import logging
from app.core.config import settings  

router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.WARNING)


@router.get(
    "/", 
    response_model=List[schemas.Document],
    summary="Retrieve all documents",
    description="Fetches a list of all documents uploaded by the authenticated user."
)
async def read_documents(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves a list of documents uploaded by the user.

    Args:
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        db (AsyncSession): The database session.
        current_user (User): The authenticated user.

    Returns:
        List[Document]: A list of documents.
    """
    logger.info(f"User {current_user.id} is requesting documents with skip={skip} and limit={limit}")

    try:
        documents = await crud.crud_document.get_documents(db=db, owner_id=current_user.id, skip=skip, limit=limit)
        logger.info(f"Fetched {len(documents)} documents for user {current_user.id}")
    except Exception as e:
        logger.error(f"Failed to fetch documents for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch documents."
        )
    return documents


@router.get(
    "/{document_id}", 
    response_model=schemas.Document,
    summary="Retrieve a specific document",
    description="Fetches details of a specific document by its ID."
)
async def read_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves a specific document by ID.

    Args:
        document_id (int): The ID of the document.
        db (AsyncSession): The database session.
        current_user (User): The authenticated user.

    Returns:
        Document: The requested document.
    """
    logger.info(f"User {current_user.id} is requesting document with ID {document_id}")

    try:
        document = await crud.crud_document.get_document(db=db, document_id=document_id, user_id=current_user.id)
        if document is None:
            logger.warning(f"Document {document_id} not found for user {current_user.id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        logger.info(f"Fetched document {document_id} for user {current_user.id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch document {document_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch document."
        )
    return document


@router.put(
    "/{document_id}", 
    response_model=schemas.Document,
    summary="Update an existing document",
    description="Updates the metadata and/or file of an existing document."
)
async def update_document(
    document_id: int,
    document_in: schemas.DocumentUpdate,  # Assuming you have a separate update schema
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates an existing document.

    Args:
        document_id (int): The ID of the document to update.
        document_in (DocumentUpdate): The updated document data.
        file (UploadFile, optional): A new file to replace the existing one.
        db (AsyncSession): The database session.
        current_user (User): The authenticated user.

    Returns:
        Document: The updated document.
    """
    logger.info(f"User {current_user.id} is attempting to update document {document_id}")

    try:
        document = await crud.crud_document.get_document(db=db, document_id=document_id, user_id=current_user.id)
        if document is None:
            logger.warning(f"Document {document_id} not found for user {current_user.id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        logger.info(f"Document {document_id} found for update by user {current_user.id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve document {document_id} for update: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document for update."
        )

    if file:
        logger.info(f"User {current_user.id} is uploading a new file for document {document_id}")
        if not allowed_file(file.filename):
            logger.warning(f"Unsupported file type attempted during update: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Allowed types: png, jpg, jpeg, pdf."
            )
        # Define user-specific upload directory
        user_upload_dir = os.path.join(UPLOAD_DIRECTORY, str(current_user.id))
        os.makedirs(user_upload_dir, exist_ok=True)

        # Save the new file asynchronously
        try:
            new_file_path = await save_upload_file(file, destination=user_upload_dir)
            logger.info(f"New file saved to {new_file_path} for document {document_id}")
        except Exception as e:
            logger.error(f"Failed to save new file during update for document {document_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save new file."
            )

        # Optionally, delete the old file
        if os.path.exists(document.file_url):
            try:
                os.remove(document.file_url)
                logger.info(f"Old file {document.file_url} deleted for document {document_id}")
            except Exception as e:
                logger.error(f"Failed to delete old file {document.file_url} for document {document_id}: {e}")
                # Decide whether to continue or not; here, we'll continue

        # Update the document_in with new file information
        document_in.file_url = new_file_path
        document_in.filename = file.filename

    # Update the document entry in the database
    try:
        updated_document = await crud.crud_document.update_document(db=db, db_document=document, document_in=document_in)
        logger.info(f"Document {document_id} updated successfully by user {current_user.id}")
    except Exception as e:
        logger.error(f"Failed to update document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update document."
        )

    return updated_document


@router.delete(
    "/{document_id}",
    response_model=schemas.DocumentDeleteResponse,
)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):    
    # Delete the document without fetching it
    try:
        await crud.crud_document.delete_document(
            db=db,
            document_id=document_id,
            owner_id=current_user.id
        )        
    except Exception as e:        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document."
        )

    return {"id": document_id, "message": "Document deleted successfully."}