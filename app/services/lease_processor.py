# app/services/lease_processor.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional
from app import schemas, crud
from app.services.document_processor import extract_text_from_file
from app.services.openai.openai_document import OpenAIService
from app.services.mapping_functions import parse_json, map_lease_data
from io import BytesIO
import json
import logging
from datetime import datetime
from app.utils.timing import log_timing

logger = logging.getLogger(__name__)

@log_timing("Lease Processing")
async def process_lease_upload(
    file_content: bytes,
    filename: str,
    property_id: Optional[int],
    document_type: str,
    db: AsyncSession,
    owner_id: int
):
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
    mapped_data = map_lease_data(parsed_data)    

    # Handle property creation/retrieval
    final_property_id = property_id
    if not final_property_id:
        # Extract property info
        property_info = mapped_data.pop('property_info', {})
        if not property_info.get('address'):
            raise ValueError("Property address is required when no property_id is provided")

        # Check if property exists for this owner
        existing_property = await crud.crud_property.get_property_by_address(
            db=db,
            address=property_info['address'],
            owner_id=owner_id
        )

        if existing_property:
            final_property_id = existing_property.id
        else:
            # Create new property
            try:
                property_in = schemas.PropertyCreate(**property_info)
                new_property = await crud.crud_property.create_with_owner(
                    db=db,
                    obj_in=property_in,
                    owner_id=owner_id
                )
                final_property_id = new_property.id
            except Exception as e:
                raise ValueError(f"Error creating property: {str(e)}")
    else:
            # If we have a property_id, still remove property_info if it exists
            _ = mapped_data.pop('property_info', None)

            
    # Update mapped_data with final property_id
    mapped_data['property_id'] = final_property_id


    # Extract tenant_info if present
    tenant_info = mapped_data.get('tenant_info', None)   
    if tenant_info:
        tenant_info['property_id'] = final_property_id

    # Handle tenant creation or retrieval
    tenant_id = None
    tenant = None
    if tenant_info:
        # Check if tenant already exists based on name and owner_id
        tenant = await crud.crud_tenant.get_tenant_by_name_and_landlord(
            db=db,
            first_name=tenant_info.get('first_name'),
            last_name=tenant_info.get('last_name'),
            landlord=tenant_info.get('landlord'),
            owner_id=owner_id
        )
        if tenant:
            tenant_id = tenant.id
        else:
            # Create a tenant
            tenant_in = schemas.TenantCreate(**tenant_info)
            tenant = await crud.crud_tenant.create_tenant(
                db=db,
                tenant_in=tenant_in,
                owner_id=owner_id
            )
            tenant_id = tenant.id

    # Include property_id and tenant_id in mapped_data
    mapped_data['property_id'] = final_property_id 

    # Create LeaseCreate schema
    try:        
        lease_in = schemas.LeaseCreate(**mapped_data)        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating lease data: {str(e)}"
        )

    # Create the lease in the database
    lease_id = None
    try:     
        lease = await crud.crud_lease.create_lease(
            db=db,
            lease_in=lease_in,
            owner_id=owner_id
        )
        lease_id = lease.id
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )    

    # Extract lease_type, description if present
    lease_type = mapped_data.get('lease_type', None)  
    description = mapped_data.get('description', None)  

    # Handle document creation or retrieval
    document_id = None    
    document_in = schemas.DocumentCreate(
        property_id=final_property_id,
        lease_id=lease_id,
        tenant_id=tenant_id,
        document_type=lease_type,
        description=description
    )    

    logger.info(document_in)
    document = await crud.crud_document.create_document(
        db=db,
        document_in=document_in,
        owner_id=owner_id
    )


    property = await crud.crud_property.get_property_by_id(
        db=db,
        property_id=final_property_id,
        owner_id=owner_id
    )
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found or you do not have access to this property."
        )

    # Link the lease to the document, tenant, and property
    lease.property = property
    lease.document = document    
    tenant.lease = lease
    tenant.property = property
    document.lease = lease
    document.property = property    

    db.add(tenant)

    await db.commit()    

    # Refresh the lease to ensure all relationships are loaded
    await db.refresh(lease)

    # Map to Pydantic schema before returning
    try:
            lease_schema = schemas.Lease.model_validate(lease, from_attributes=True)
            return lease_schema
    except Exception as e:
        logger.error(f"Error serializing lease: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while serializing the lease data."
        )
