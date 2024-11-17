# app/crud/crud_lease.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models.lease import Lease
from app.models.property import Property
from app.schemas.lease import LeaseCreate, LeaseUpdate
from app.services.mapping_functions import map_lease_data

async def create_lease(
    db: AsyncSession,
    lease_in: LeaseCreate,
    owner_id: int
) -> Lease:
    # Verify that the property exists and belongs to the owner
    result = await db.execute(
        select(Property)
        .filter(Property.id == lease_in.property_id)
        .filter(Property.owner_id == owner_id)
    )
    property = result.scalars().first()
    if not property:
        raise ValueError("Property not found or you do not have permission to access this property.")

    # Create the lease instance directly from lease_in
    db_lease = Lease(**lease_in.dict())
    db.add(db_lease)
    try:
        await db.commit()
        await db.refresh(db_lease)
    except IntegrityError as e:
        await db.rollback()
        raise ValueError("An error occurred while saving the lease: " + str(e))
    return db_lease

# Retrieve leases by owner
async def get_leases(
    db: AsyncSession,
    owner_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Lease]:
    result = await db.execute(
        select(Lease)
        .join(Property)
        .filter(Property.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

# Get a single lease by ID, ensuring ownership
async def get_lease(
    db: AsyncSession,
    lease_id: int,
    owner_id: int
) -> Lease:
    result = await db.execute(
        select(Lease)
        .join(Property)
        .filter(Lease.id == lease_id)
        .filter(Property.owner_id == owner_id)
    )
    return result.scalars().first()

# Update a lease
async def update_lease(
    db: AsyncSession,
    lease: Lease,
    lease_in: LeaseUpdate
) -> Lease:
    for key, value in lease_in.dict(exclude_unset=True).items():
        setattr(lease, key, value)
    try:
        await db.commit()
        await db.refresh(lease)
    except IntegrityError as e:
        await db.rollback()
        raise ValueError("An error occurred while updating the lease: " + str(e))
    return lease

# Delete a lease
async def delete_lease(
    db: AsyncSession,
    lease_id: int,
    owner_id: int
) -> Lease:
    lease = await get_lease(db=db, lease_id=lease_id, owner_id=owner_id)
    if not lease:
        raise ValueError("Lease not found or you do not have permission to delete this lease.")
    await db.delete(lease)
    await db.commit()
    return lease
