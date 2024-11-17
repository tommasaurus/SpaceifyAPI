from fastapi import FastAPI
from app.api.endpoints import (
    user,
    property,
    tenant,
    lease,
    payment,
    expense,
    income,
    invoice,
    vendor,
    contract,
    document,
    utility,
    chat,
    processor
)
from app.api.endpoints.auth_routes import router as auth_router
from app.db.database import engine, Base
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Import all models
from app.models import (
    user as user_model,
    property as property_model,
    tenant as tenant_model,
    lease as lease_model,
    payment as payment_model,
    expense as expense_model,
    income as income_model,
    vendor as vendor_model,
    contract as contract_model,
    document as document_model,
    utility as utility_model,
)
from app.models.invoice import invoice as invoice_model
from app.models.invoice import invoice_item as invoice_item_model

app = FastAPI(
    title="Spaceify",
    description="An API for managing properties, leases, tenants, and financials.",
    version="1.0.0"
)

# Include authentication router
app.include_router(auth_router, prefix="/auth", tags=["auth"])

# Include routers for other endpoints
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(property.router, prefix="/properties", tags=["properties"])
app.include_router(tenant.router, prefix="/tenants", tags=["tenants"])
app.include_router(lease.router, prefix="/leases", tags=["leases"])
app.include_router(payment.router, prefix="/payments", tags=["payments"])
app.include_router(expense.router, prefix="/expenses", tags=["expenses"])
app.include_router(income.router, prefix="/incomes", tags=["incomes"])
app.include_router(invoice.router, prefix="/invoices", tags=["invoices"])
app.include_router(vendor.router, prefix="/vendors", tags=["vendors"])
app.include_router(contract.router, prefix="/contracts", tags=["contracts"])
app.include_router(document.router, prefix="/documents", tags=["documents"])
app.include_router(utility.router, prefix="/utilities", tags=["utilities"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(processor.router, prefix="/processor", tags=["processor"])

# Database initialization
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
