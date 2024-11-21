# app/api/endpoints/chat.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.schemas.chat import ChatMessage, ChatResponse
from app.services.openai.copilot import OpenAIService
from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.property import Property
from app.models.expense import Expense
import difflib
import logging


router = APIRouter()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/echo", response_model=ChatResponse)
async def echo_message(
    chat_message: ChatMessage,
    current_user: User = Depends(get_current_user)
):
    response = f"{chat_message.message} echo"
    return {"response": response}

@router.post("/copilot", response_model=ChatResponse)
async def copilot_message(
    chat_message: ChatMessage,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    openai_service = OpenAIService()

    # Use OpenAI to parse the intent and entities
    intent_and_entities = await openai_service.parse_intent_and_entities(chat_message.message)

    if not intent_and_entities:
        return {"response": "I'm sorry, I didn't understand that."}

    intent = intent_and_entities.get('intent')
    entities = intent_and_entities.get('entities', {})

    # Map intents to action functions
    intent_action_mapping = {
        "get_highest_expense_by_property": handle_highest_expense_by_property,
        "get_highest_expense_across_properties": handle_highest_expense_across_properties,
        "list_properties": handle_list_properties,
        # Add more intents as needed
    }


    action_function = intent_action_mapping.get(intent)
    if action_function:
        response_text = await action_function(entities, db, current_user)
    else:
        response_text = "I'm sorry, I didn't understand that."

    return {"response": response_text}

async def handle_highest_expense_by_property(entities, db: AsyncSession, current_user: User):
    property_name = entities.get('property_name')

    if not property_name:
        return "Please specify the property name."

    # Retrieve all properties owned by the user
    result = await db.execute(
        select(Property)
        .filter(Property.owner_id == current_user.id)
    )
    properties = result.scalars().all()

    if not properties:
        return "You do not have any properties registered."

    # Create a list of property names
    property_names = [prop.address for prop in properties]

    # Use difflib to find close matches
    matches = difflib.get_close_matches(property_name, property_names, n=3, cutoff=0.5)

    if not matches:
        return f"No properties found matching '{property_name}'. Here are your properties:\n" + \
               "\n".join([f"- {name}" for name in property_names])

    if len(matches) > 1:
        matches_list = "\n".join([f"- {name}" for name in matches])
        return f"Multiple properties match '{property_name}'. Did you mean:\n{matches_list}"

    # Exactly one match found
    matched_property_name = matches[0]

    # Get the property object
    property = next((prop for prop in properties if prop.address == matched_property_name), None)

    # Get the expense with the highest amount for this property
    result = await db.execute(
        select(Expense)
        .filter(Expense.property_id == property.id)
        .order_by(Expense.amount.desc())
        .limit(1)
    )
    expense = result.scalars().first()

    if not expense:
        return f"No expenses found for property '{property.address}'."

    response = (
        f"The highest expense for property '{property.address}' is ${expense.amount:.2f} "
        f"on {expense.transaction_date}, for '{expense.description}'."
    )
    return response


async def handle_highest_expense_across_properties(entities, db: AsyncSession, current_user: User):
    # Get the expense with the highest amount across all properties owned by the user
    result = await db.execute(
        select(Expense, Property)
        .join(Property, Property.id == Expense.property_id)
        .filter(Property.owner_id == current_user.id)
        .order_by(Expense.amount.desc())
        .limit(1)
    )
    row = result.first()
      
    if not row:
        return "No expenses found for your properties."

    expense, property = row

    response = (
        f"The highest expense across all your properties is ${expense.amount:.2f} "
        f"for property '{property.address}' on {expense.transaction_date}, for '{expense.description}'."
    )
    return response

async def handle_list_properties(entities, db: AsyncSession, current_user: User):
    # Retrieve all properties owned by the user
    result = await db.execute(
        select(Property)
        .filter(Property.owner_id == current_user.id)
    )
    properties = result.scalars().all()

    if not properties:
        return "You do not have any properties registered."

    property_list = "\n".join([f"- {prop.address}" for prop in properties])

    response = f"Here are your properties:\n{property_list}"

    return response
