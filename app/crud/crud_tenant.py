# app/crud/crud_tenant.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.tenant import Tenant
from app.models.property import Property
from app.schemas.tenant import TenantResponse, TenantCreate, TenantUpdate

class CRUDTenant:
    async def get_tenant(
        self, db: AsyncSession, tenant_id: int, owner_id: int
    ) -> Optional[Tenant]:
        result = await db.execute(
            select(Tenant)
            .options(
                selectinload(Tenant.property),
                selectinload(Tenant.lease),
            )
            .join(Tenant.property)
            .filter(Tenant.id == tenant_id)
            .filter(Property.owner_id == owner_id)
        )
        return result.scalars().first()

    async def get_tenants(
        self, db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[TenantResponse]:
        result = await db.execute(
            select(Tenant)
            .options(
                selectinload(Tenant.property),
                selectinload(Tenant.lease),
            )
            .filter(Tenant.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        tenants = result.scalars().all()
        return tenants


    async def get_tenant_by_name_and_landlord(
        self,
        db: AsyncSession,
        first_name: str,
        last_name: str,
        landlord: str,
        owner_id: int
    ) -> Optional[Tenant]:
        """
        Retrieves a tenant based on normalized first name, last name, and landlord.
        Normalization includes removing spaces and converting to lowercase.
        """
        normalized_first_name = func.lower(func.replace(Tenant.first_name, ' ', ''))
        normalized_last_name = func.lower(func.replace(Tenant.last_name, ' ', ''))
        normalized_landlord = func.lower(func.replace(Tenant.landlord, ' ', ''))
        normalized_input_first_name = first_name.replace(' ', '').lower()
        normalized_input_last_name = last_name.replace(' ', '').lower()
        normalized_input_landlord = landlord.replace(' ', '').lower()

        result = await db.execute(
            select(Tenant)
            .join(Tenant.lease)
            .join(Property)
            .filter(Property.owner_id == owner_id)
            .filter(normalized_first_name == normalized_input_first_name)
            .filter(normalized_last_name == normalized_input_last_name)
            .filter(normalized_landlord == normalized_input_landlord)
        )
        return result.scalars().first()

    async def get_tenant_by_id(
        self, db: AsyncSession, tenant_id: int
    ) -> Optional[Tenant]:
        result = await db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        return result.scalars().first()
    
    async def create_tenant(
        self, db: AsyncSession, *, tenant_in: TenantCreate, owner_id: int
    ) -> Tenant:
        tenant_data = tenant_in.dict()
        tenant_data['owner_id'] = owner_id  # Set owner_id
        tenant = Tenant(**tenant_data)
        db.add(tenant)
        try:
            await db.commit()
            await db.refresh(tenant)
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while creating the tenant: " + str(e))

        # Eagerly load relationships
        await db.refresh(tenant)
        return tenant

    async def create_tenant_manual(
        self, db: AsyncSession, *, tenant_in: TenantCreate, owner_id: int
    ) -> TenantResponse:
        tenant_data = tenant_in.dict()
        tenant_data['owner_id'] = owner_id  # Set owner_id
        tenant = Tenant(**tenant_data)
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)

        # Re-fetch the tenant with relationships eagerly loaded
        result = await db.execute(
            select(Tenant)
            .options(
                selectinload(Tenant.property),
                selectinload(Tenant.lease),
            )
            .filter(Tenant.id == tenant.id)
        )
        tenant_with_relationships = result.scalars().first()

        return TenantResponse.from_orm(tenant_with_relationships)


    async def update_tenant(
        self, db: AsyncSession, db_tenant: Tenant, tenant_in: TenantUpdate
    ) -> Tenant:
        update_data = tenant_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_tenant, key, value)
        try:
            await db.commit()
            await db.refresh(db_tenant)
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while updating the tenant: " + str(e))
        return db_tenant

    async def delete_tenant(
        self, db: AsyncSession, tenant_id: int, owner_id: int
    ) -> Optional[Tenant]:
        # First find the tenant directly without joining property
        result = await db.execute(
            select(Tenant)
            .filter(Tenant.id == tenant_id)
            .filter(Tenant.owner_id == owner_id)
        )
        db_tenant = result.scalars().first()
        
        if db_tenant:
            await db.delete(db_tenant)
            try:
                await db.commit()
            except IntegrityError as e:
                await db.rollback()
                raise ValueError("An error occurred while deleting the tenant: " + str(e))
        return db_tenant

# Initialize the CRUD object
crud_tenant = CRUDTenant()
