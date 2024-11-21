# app/services/invoice_processor.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app import schemas, crud
from app.services.document_processor import extract_text_from_file
from app.services.openai.openai_document import OpenAIService
from app.services.mapping_functions import parse_json, map_invoice_data
from io import BytesIO
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def process_invoice_upload(
    file_content: bytes,
    filename: str,
    property_id: int,
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
    mapped_data = map_invoice_data(parsed_data)

    # Include property_id in mapped_data
    mapped_data['property_id'] = property_id

    # Extract vendor_info if present
    vendor_info = mapped_data.pop('vendor_info', None)

    # Handle vendor creation or retrieval
    vendor_id = None
    if vendor_info:
        # Check if vendor already exists based on name and owner_id
        existing_vendor = await crud.crud_vendor.get_vendor_by_name(
            db=db,
            name=vendor_info.get('name'),
            owner_id=owner_id
        )
        if existing_vendor:
            vendor_id = existing_vendor.id
        else:
            # Create a new vendor
            vendor_in = schemas.VendorCreate(**vendor_info)
            new_vendor = await crud.crud_vendor.create_vendor(
                db=db,
                vendor_in=vendor_in,
                owner_id=owner_id
            )
            vendor_id = new_vendor.id

    # Set vendor_id in mapped_data if available
    if vendor_id:
        mapped_data['vendor_id'] = vendor_id

    # Create InvoiceCreate schema
    invoice_in = schemas.InvoiceCreate(**mapped_data)

    # Create the invoice in the database
    invoice = await crud.crud_invoice.create_invoice(
        db=db,
        invoice_in=invoice_in,
        owner_id=owner_id
    )

    # Capture the invoice ID immediately
    invoice_id = invoice.id

    # Optionally create a document entry
    document_in = schemas.DocumentCreate(
        property_id=property_id,
        invoice_id=invoice_id,
        document_type=document_type,
        description=invoice_in.description
    )
    document = await crud.crud_document.create_document(
        db=db,
        document_in=document_in,
        owner_id=owner_id
    )

    # Optionally create an expense entry
    expense_in = schemas.ExpenseCreate(
        property_id=property_id,
        vendor_id=vendor_id,
        invoice_id=invoice_id,
        category="Invoice Expense",
        amount=invoice_in.amount,
        transaction_date=invoice_in.invoice_date or datetime.utcnow().date(),
        description=invoice_in.description
    )
    expense = await crud.crud_expense.create_expense(
        db=db,
        expense_in=expense_in,
        owner_id=owner_id
    )

    # Link the invoice to the document and expense
    invoice.document = document
    invoice.expense = expense
    await db.commit()

    # Re-fetch the invoice to ensure relationships are loaded
    invoice = await crud.crud_invoice.get_invoice(invoice_id=invoice_id, owner_id=owner_id, db=db)
    if not invoice:
        raise ValueError("Failed to load invoice after creation.")

    try:
            invoice_schema = schemas.Invoice.model_validate(invoice, from_attributes=True)
            return invoice_schema
    except Exception as e:
        logger.error(f"Error serializing invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while serializing the invoice data."
        )
