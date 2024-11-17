# app/crud/crud_invoice.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from typing import List
from app.models.property import Property
from app.models.vendor import Vendor
from app.models.invoice.invoice import Invoice
from app.models.invoice.invoice_item import InvoiceItem
from app.schemas.invoice.invoice import InvoiceCreate, InvoiceUpdate

class CRUDInvoice:
    async def create_invoice(
        self,
        db: AsyncSession,
        invoice_in: InvoiceCreate,
        owner_id: int
    ) -> Invoice:
        # Verify that the property exists and belongs to the owner
        result = await db.execute(
            select(Property)
            .filter(Property.id == invoice_in.property_id)
            .filter(Property.owner_id == owner_id)
        )
        property = result.scalars().first()
        if not property:
            raise ValueError("Property not found or you do not have permission to access this property.")

        # Optionally verify that the vendor exists, if vendor_id is provided
        if invoice_in.vendor_id:
            result = await db.execute(
                select(Vendor)
                .filter(Vendor.id == invoice_in.vendor_id)
            )
            vendor = result.scalars().first()
            if not vendor:
                raise ValueError("Vendor not found.")

        # Create the invoice instance directly from invoice_in, excluding line_items
        invoice_data = invoice_in.dict(exclude={"line_items"})
        db_invoice = Invoice(**invoice_data)

        # Calculate remaining_balance
        db_invoice.remaining_balance = round(db_invoice.amount - (db_invoice.paid_amount or 0.0), 2)

        # Add line items if any
        if invoice_in.line_items:
            for item_in in invoice_in.line_items:
                item_data = item_in.dict()
                db_item = InvoiceItem(**item_data)
                db_invoice.line_items.append(db_item)

        db.add(db_invoice)
        try:
            await db.commit()
            await db.refresh(db_invoice)
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while saving the invoice: " + str(e))
        return db_invoice

    async def get_invoices(
        self,
        db: AsyncSession,
        owner_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Invoice]:
        result = await db.execute(
            select(Invoice)
            .options(joinedload(Invoice.line_items))  # Eagerly load line_items
            .join(Property)
            .filter(Property.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return result.unique().scalars().all()

    async def get_invoice(
        self,
        db: AsyncSession,
        invoice_id: int,
        owner_id: int
    ) -> Invoice:
        result = await db.execute(
            select(Invoice)
            .options(joinedload(Invoice.line_items))  # Eagerly load line_items
            .join(Property)
            .filter(Invoice.id == invoice_id)
            .filter(Property.owner_id == owner_id)
        )
        return result.scalars().first()

    async def update_invoice(
        self,
        db: AsyncSession,
        invoice: Invoice,
        invoice_in: InvoiceUpdate
    ) -> Invoice:
        for key, value in invoice_in.dict(exclude_unset=True).items():
            setattr(invoice, key, value)
        # Recalculate remaining_balance if amount or paid_amount changed
        if 'amount' in invoice_in.dict(exclude_unset=True) or 'paid_amount' in invoice_in.dict(exclude_unset=True):
            invoice.remaining_balance = invoice.amount - (invoice.paid_amount or 0.0)
        try:
            await db.commit()
            await db.refresh(invoice)
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while updating the invoice: " + str(e))
        return invoice

    async def delete_invoice(
        self,
        db: AsyncSession,
        invoice_id: int,
        owner_id: int
    ) -> Invoice:
        invoice = await self.get_invoice(db=db, invoice_id=invoice_id, owner_id=owner_id)
        if not invoice:
            raise ValueError("Invoice not found or you do not have permission to delete this invoice.")
        await db.delete(invoice)
        await db.commit()
        return invoice


# Initialize the CRUD object
crud_invoice = CRUDInvoice()