# app/services/mapping_functions.py

from datetime import datetime, date
import json
import logging

# Initialize logger for this module
logger = logging.getLogger(__name__)

def normalize_keys(d):
    """
    Recursively normalizes the keys of the dictionary: strip whitespace, convert to lowercase,
    replace spaces with underscores.
    """
    new_dict = {}
    for key, value in d.items():
        if isinstance(key, str):
            new_key = key.strip().lower().replace(' ', '_')
        else:
            new_key = key
        if isinstance(value, dict):
            new_value = normalize_keys(value)
        elif isinstance(value, list):
            new_value = [normalize_keys(item) if isinstance(item, dict) else item for item in value]
        else:
            new_value = value
        new_dict[new_key] = new_value
    return new_dict

# Helper function to safely get nested values
def get_nested_value(data, keys, default="Not Found"):
    """
    Safely retrieves a nested value from a dictionary.
    """
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return default
    return data

def clean_currency(value):
    if isinstance(value, str):        
        value = value.replace('$', '').replace(',', '').strip()
        try:
            return float(value)
        except ValueError:
            return None  # or 0.0 if you prefer
    return value

def parse_date(value):
    if isinstance(value, str):
        try:
            # Try parsing MM/DD/YYYY format
            return datetime.strptime(value, '%m/%d/%Y').date()
        except ValueError:
            try:
                # Try parsing YYYY-MM-DD format
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                logger.warning(f"Failed to parse date: {value}")
                return None  # Date parsing failed
    elif isinstance(value, date):
        return value
    else:
        logger.warning(f"Invalid date value: {value}")
        return None


def parse_json(raw_json: str) -> dict:
    """
    Parses and validates the JSON string response from OpenAI, normalizes keys,
    and ensures consistent structure for mapping.

    Args:
        raw_json (str): The raw JSON string from OpenAI.

    Returns:
        dict: A structured dictionary with normalized keys.
    """
    try:
        extracted_data = json.loads(raw_json)
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON response.")
        return {}

    # Normalize keys
    parsed_data = normalize_keys(extracted_data)
    return parsed_data

def map_tenant_data(tenant_info: list) -> list:
    """
    Maps parsed tenant data to the Tenant model fields for a single tenant.

    Args:
        tenant_info (Dict[str, Any]): Tenant information dictionary parsed from JSON.

    Returns:
        Dict[str, Any]: Mapped tenant data ready for Tenant creation.
    """
               
    tenant_data = {
        "first_name": tenant_info.get("first_name", "Not Found").split()[0] if tenant_info.get("first_name") else "Not Found",
        "last_name": tenant_info.get("last_name", "Not Found").split()[-1] if tenant_info.get("last_name") else "Not Found",
        "email": tenant_info.get("email", None) if tenant_info.get("email") != "Not Found" else None,
        "phone_number": tenant_info.get("phone_number", None),
        "date_of_birth": parse_date(tenant_info.get("date_of_birth", None)),
        "landlord": tenant_info.get("landlord", None),
        "address": tenant_info.get("address", None),
        "status": tenant_info.get("status", "current")
    }        

    return tenant_data

def map_property_data(property_info: dict) -> dict:
    """
    Maps property information extracted from lease document to Property model fields.
    Ensures numeric fields are None when not found or invalid.
    
    Args:
        property_info (dict): Property information dictionary parsed from JSON
        
    Returns:
        dict: Mapped property data ready for Property creation
    """
    # Helper function to convert to int or None
    def to_int_or_none(value):
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(value)
            except (ValueError, TypeError):
                return None
        return None

    property_data = {
        "address": property_info.get("address", "Not Found"),
        "num_bedrooms": to_int_or_none(property_info.get("num_bedrooms")),
        "num_bathrooms": to_int_or_none(property_info.get("num_bathrooms")),
        "num_floors": to_int_or_none(property_info.get("num_floors")),
        "is_commercial": property_info.get("is_commercial", False),
        "property_type": property_info.get("property_type", "residential")
    }
    
    return property_data

def map_lease_data(parsed_data: dict) -> dict:
    """
    Maps the parsed data to the Lease model fields.

    Args:
        parsed_data (dict): The data parsed by `parse_json`.

    Returns:
        dict: A dictionary of Lease fields ready to be used for creation.
    """

    property_info = parsed_data.get("property_information", {})

    lease_data = {
        "lease_type": parsed_data.get("lease_type", "Not Found"),
        "description": parsed_data.get("description", "Not Found"),
        "rent_amount_total": clean_currency(get_nested_value(parsed_data, ["rent_amount", "total"], "0")),
        "rent_amount_monthly": clean_currency(get_nested_value(parsed_data, ["rent_amount", "monthly_installment"], "0")),
        "security_deposit_amount": get_nested_value(parsed_data, ["security_deposit", "amount"], "Not Found"),
        "security_deposit_held_by": get_nested_value(parsed_data, ["security_deposit", "held_by"], "Not Found"),
        "start_date": parse_date(parsed_data.get("start_date", None)),
        "end_date": parse_date(parsed_data.get("end_date", None)),
        "payment_frequency": parsed_data.get("payment_frequency", "Monthly"),
        "tenant_info": map_tenant_data(parsed_data.get("tenant_information", {})),
        "special_lease_terms": parsed_data.get("special_lease_terms", {}),
        "property_info": map_property_data(property_info),
        "is_active": True  # Default value; adjust if necessary
    }

    return lease_data

def map_invoice_data(parsed_data: dict) -> dict:
    """
    Maps the parsed data to the Invoice model fields, including line items.
    """
    try:
        amount = clean_currency(parsed_data.get("amount", "0"))
        paid_amount = clean_currency(parsed_data.get("paid_amount", "0"))

        # Parse dates
        invoice_date = parse_date(parsed_data.get("invoice_date"))
        due_date = parse_date(parsed_data.get("due_date"))

        # Process line items
        line_items_data = []
        line_items = parsed_data.get("line_items", [])
        for item in line_items:
            item_description = get_nested_value(item, ["description"], "No description")
            quantity = clean_currency(get_nested_value(item, ["quantity"], "1")) or None
            unit_price = clean_currency(get_nested_value(item, ["unit_price"], "0")) or None
            total_price = clean_currency(get_nested_value(item, ["total_price"], "0")) or None

            line_item = {
                "description": item_description,
                "quantity": float(quantity) if isinstance(quantity, (int, float)) else None,
                "unit_price": float(unit_price) if isinstance(unit_price, (int, float)) else None,
                "total_price": float(total_price) if isinstance(total_price, (int, float)) else None,
            }
            line_items_data.append(line_item)

        invoice_data = {
            "invoice_number": parsed_data.get("invoice_number") or None,
            "amount": amount if amount is not None else 0.0,
            "paid_amount": paid_amount if paid_amount is not None else 0.0,
            "remaining_balance": round((amount if amount else 0.0) - (paid_amount if paid_amount else 0.0), 2),
            "invoice_date": invoice_date.isoformat() if invoice_date else None,
            "due_date": due_date.isoformat() if due_date else None,
            "status": parsed_data.get("status") or "Unpaid",
            "description": parsed_data.get("description") or None,
            "vendor_info": parsed_data.get("vendor_information", {}),
            "line_items": line_items_data,
        }
    except Exception as e:
        logger.error(f"Error mapping invoice data: {e}")
        invoice_data = {}  # Return an empty dict in case of an error
    return invoice_data

def map_contract_data(parsed_data: dict) -> dict:
    """
    Maps the parsed data to the Contract model fields, handling multiple parties.

    Args:
        parsed_data (dict): The data parsed by `parse_json`.

    Returns:
        dict: A dictionary of Contract fields ready to be used for creation.
    """
    try:
        # Parse dates
        start_date = parse_date(parsed_data.get("start_date"))
        end_date = parse_date(parsed_data.get("end_date"))

        # Handle multiple parties involved
        parties_involved = parsed_data.get("parties_involved", [])
        if not isinstance(parties_involved, list):
            parties_involved = [parties_involved]

        # Map vendor information
        vendor_info = parsed_data.get("vendor_information", {})
        vendor_data = {
            "name": vendor_info.get("name", "Not Found"),
            "address": vendor_info.get("address"),
            "contact_person": vendor_info.get("contact_person"),
            "phone_number": vendor_info.get("phone_number"),
            "email": vendor_info.get("email") if vendor_info.get("email") != "Not Found" else None
        }

        # Map terms
        terms = parsed_data.get("terms", {})

        is_active = parsed_data.get("is_active", True)
        if isinstance(is_active, str):
            is_active = is_active.strip().lower() == "true"
        elif isinstance(is_active, (int, float)):
            is_active = bool(is_active)
        elif not isinstance(is_active, bool):
            is_active = True
        else:
            is_active = False

        contract_data = {
            "contract_type": parsed_data.get("contract_type", "Not Found"),
            "description": parsed_data.get("description", "Not Found"),
            "start_date": start_date,
            "end_date": end_date,
            "terms": terms,
            "is_active": is_active,
            "vendor_info": vendor_data,
            "parties_involved": parties_involved  # Store as JSON
        }
    except Exception as e:
        logger.error(f"Error mapping contract data: {e}")
        contract_data = {}
    return contract_data