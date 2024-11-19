# app/api/endpoints/contract.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import schemas, crud
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.contract_processor import process_contract_upload

router = APIRouter()

@router.post("/upload", response_model=schemas.Contract)
async def upload_contract(
    property_id: int = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

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
        
    try:
        file_content = await file.read()
        contract = await process_contract_upload(
            file_content=file_content,
            filename=file.filename,
            property_id=property_id,
            document_type=document_type,
            db=db,
            owner_id=current_user.id
        )
        return contract
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=schemas.Contract)
async def create_contract(
    contract_in: schemas.ContractCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        contract = await crud.crud_contract.create_contract(db=db, contract_in=contract_in, owner_id=current_user.id)
        return contract
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.Contract])
async def read_contracts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contracts = await crud.crud_contract.get_contracts(db=db, owner_id=current_user.id, skip=skip, limit=limit)
    return contracts

@router.get("/{contract_id}", response_model=schemas.Contract)
async def read_contract(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = await crud.crud_contract.get_contract(db=db, contract_id=contract_id, owner_id=current_user.id)
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract

@router.put("/{contract_id}", response_model=schemas.Contract)
async def update_contract(
    contract_id: int,
    contract_in: schemas.ContractUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = await crud.crud_contract.get_contract(db=db, contract_id=contract_id, owner_id=current_user.id)
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    try:
        updated_contract = await crud.crud_contract.update_contract(db=db, db_contract=contract, contract_in=contract_in)
        return updated_contract
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{contract_id}", response_model=schemas.Contract)
async def delete_contract(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch the contract with relationships eagerly loaded
    contract = await crud.crud_contract.get_contract(
        db=db,
        contract_id=contract_id,
        owner_id=current_user.id
    )
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    # Prepare the response data before deletion
    contract_response = schemas.Contract.from_orm(contract)

    # Delete the contract
    try:
        await crud.crud_contract.delete_contract(
            db=db,
            contract_id=contract_id,
            owner_id=current_user.id
        )
    except ValueError as e:
        # Log the error
        logger.error(f"Failed to delete contract {contract_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    # Return the prepared response
    return contract_response
