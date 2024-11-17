# app/crud/crud_document.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlalchemy import update  
from typing import List, Optional
from app.models.document import Document
from app.models.property import Property
from app.schemas.document import DocumentCreate, DocumentUpdate

class CRUDDocument:
    async def get_document(self, db: AsyncSession, document_id: int, owner_id: int) -> Optional[Document]:
        """
        Retrieve a single document by its ID, ensuring it belongs to the specified user.
        Eagerly loads related relationships to prevent lazy loading during serialization.
        """
        result = await db.execute(
            select(Document)
            .options(
                selectinload(Document.property),
                selectinload(Document.lease),
                selectinload(Document.expense),
                selectinload(Document.invoice),
                selectinload(Document.contract)
            )
            .join(Property)
            .filter(Document.id == document_id)
            .filter(Property.owner_id == owner_id)
        )
        return result.scalars().first()

    async def get_documents(self, db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 100) -> List[Document]:
        """
        Retrieve a list of documents belonging to the specified user.
        Eagerly loads related relationships to prevent lazy loading during serialization.
        """
        result = await db.execute(
            select(Document)
            .options(
                selectinload(Document.property),
                selectinload(Document.lease),
                selectinload(Document.expense),
                selectinload(Document.invoice),
                selectinload(Document.contract)
            )
            .join(Property)
            .filter(Property.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_document(self, db: AsyncSession, document_in: DocumentCreate, owner_id: int) -> Document:
        """
        Create a new document after verifying ownership of the associated property.
        Eagerly loads related relationships after creation.
        """
        # Verify that the property exists and belongs to the user (if property_id is provided)
        if document_in.property_id:
            result = await db.execute(
                select(Property)
                .filter(Property.id == document_in.property_id, Property.owner_id == owner_id)
            )
            property = result.scalars().first()
            if not property:
                raise ValueError("Property not found or you do not have permission to access this property.")

        db_document = Document(**document_in.dict())
        db.add(db_document)
        try:
            await db.commit()
            # Eagerly load relationships after creation
            await db.refresh(
                db_document,
                attribute_names=["property", "lease", "expense", "invoice", "contract"]
            )
            # Alternatively, use selectinload with refresh
            # await db.refresh(db_document, attribute_names=["property", "lease", "expense", "invoice", "contract"])
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while creating the document: " + str(e))
        return db_document

    async def update_document(self, db: AsyncSession, db_document: Document, document_in: DocumentUpdate) -> Document:
        """
        Update an existing document with new data.
        Eagerly loads related relationships after update.
        """
        update_data = document_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_document, key, value)
        try:
            await db.commit()
            # Eagerly load relationships after update
            await db.refresh(
                db_document,
                attribute_names=["property", "lease", "expense", "invoice", "contract"]
            )
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while updating the document: " + str(e))
        return db_document

    async def delete_document(self, db: AsyncSession, document_id: int, owner_id: int) -> Optional[Document]:
        """
        Delete a document by its ID after verifying ownership.
        """
        db_document = await self.get_document(db, document_id, owner_id)
        if db_document:
            await db.delete(db_document)
            try:
                await db.commit()
            except IntegrityError as e:
                await db.rollback()
                raise ValueError("An error occurred while deleting the document: " + str(e))
        return db_document

    async def update_status(self, db: AsyncSession, document_id: int, status: str) -> None:
        """
        Update the status of a document.
        """
        await db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(status=status)
        )
        await db.commit()

# Initialize the CRUD object
crud_document = CRUDDocument()
