# app/services/contract_processor.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app import schemas, crud
from app.services.document_processor import extract_text_from_file
from app.services.openai.openai_document import OpenAIService
from app.services.mapping_functions import parse_json, map_contract_data
from io import BytesIO
import json
import logging

logger = logging.getLogger(__name__)

async def process_contract_upload(
    file_content: bytes,
    filename: str,
    property_id: int,
    document_type: str,
    db: AsyncSession,
    owner_id: int
):
    try:
        # Extract text from the file
        file_like = BytesIO(file_content)
        text = extract_text_from_file(file_like, filename)
        if not text:
            raise ValueError("Could not extract text from the document.")

        # Initialize OpenAIService
        openai_service = OpenAIService()
        extracted_data = await openai_service.extract_information(text, document_type)

        if not extracted_data:
            raise ValueError("Could not extract information from the document.")

        # Parse and map data
        parsed_data = parse_json(json.dumps(extracted_data))
        mapped_data = map_contract_data(parsed_data)

        # Extract vendor_info if present
        vendor_info = mapped_data.get('vendor_info', None)

        # Handle vendor creation or retrieval
        vendor_id = None
        vendor = None
        if vendor_info:
            # Check if vendor already exists based on name and owner_id
            vendor = await crud.crud_vendor.get_vendor_by_name(
                db=db,
                name=vendor_info.get('name'),
                owner_id=owner_id
            )
            if vendor:
                vendor_id = vendor.id
            else:
                # Create a vendor
                vendor_in = schemas.VendorCreate(**vendor_info)
                vendor = await crud.crud_vendor.create_vendor(
                    db=db,
                    vendor_in=vendor_in,
                    owner_id=owner_id
                )
                vendor_id = vendor.id

        # Include property_id and vendor_id in mapped_data
        mapped_data['property_id'] = property_id
        mapped_data['vendor_id'] = vendor_id

        # Create ContractCreate schema
        try:
            # Remove 'vendor_info' from mapped_data before creating ContractCreate
            contract_in_data = mapped_data.copy()
            contract_in_data.pop('vendor_info', None)
            contract_in = schemas.ContractCreate(**contract_in_data)
        except Exception as e:
            logger.error(f"Error creating ContractCreate schema: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating contract data: {str(e)}"
            )

        # Create the contract in the database
        try:
            contract = await crud.crud_contract.create_contract(
                db=db,
                contract_in=contract_in,
                owner_id=owner_id
            )
            contract_id = contract.id
            logger.info("Created contract with ID: %s", contract_id)
        except ValueError as e:
            logger.error(f"Error creating contract: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        # Handle document creation
        document_in = schemas.DocumentCreate(
            property_id=property_id,
            contract_id=contract_id,
            document_type=document_type,
            description=mapped_data.get('description', None)
        )

        document = await crud.crud_document.create_document(
            db=db,
            document_in=document_in,
            owner_id=owner_id
        )
        logger.info("Created document with ID: %s", document.id)

        # Re-fetch the contract with relationships eagerly loaded
        contract = await crud.crud_contract.get_contract(
            db=db,
            contract_id=contract_id,
            owner_id=owner_id
        )

        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found or you do not have access to this contract."
            )

        # Map to Pydantic schema before returning
        try:
            contract_schema = schemas.Contract.model_validate(contract, from_attributes=True)  # Added from_attributes=True
            return contract_schema
        except Exception as e:
            logger.error(f"Error serializing contract: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while serializing the contract data."
            )

    except Exception as e:
        logger.error(f"Unexpected error during contract upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during contract upload."
        )
