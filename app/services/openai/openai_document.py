# app/services/openai/openai_document.py

import logging
import json
from typing import Optional
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessage
from app.utils.timing import log_timing

# Import your settings or configuration module
from app.core.config import settings

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class OpenAIService:
    def __init__(self):
        # Initialize the OpenAI client
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    @log_timing("OpenAI Information Extraction")
    async def extract_information(self, text: str, document_type: str) -> dict:
        """
        Uses OpenAI's API to extract relevant information from the text based on the document type.

        Args:
            text (str): The text extracted from the document.
            document_type (str): The type of the document (e.g., 'invoice', 'lease').

        Returns:
            dict: Extracted information structured in a dictionary.
        """
        messages = self._generate_prompt_by_type(text, document_type)

        try:
            # Make an asynchronous request to OpenAI with the chat completion API
            response = await self.client.chat.completions.create(
                messages=messages,
                model="gpt-4o-mini",
                temperature=0.0,
            )

            # Extract content and remove any ```json markers
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:]  # Remove the starting ```json
            if content.endswith("```"):
                content = content[:-3]  # Remove the ending ```

            # Now attempt to parse the cleaned JSON string
            extracted_data = json.loads(content)
            return extracted_data

        except json.JSONDecodeError:
            logger.error("Error decoding JSON from OpenAI response.")
            return {}
        except Exception as e:
            logger.error(f"An error occurred while extracting information: {e}")
            return {}

    @log_timing("OpenAI Document Type Classification")
    async def determine_document_type(self, text: str) -> Optional[str]:
        """
        Uses OpenAI's API to determine the type of document based on the text.
        Args:
            text (str): The text extracted from the document.
        Returns:
            str: Determined document type.
        """
        messages = [
        {
            "role": "system",
            "content": (
                "You are an intelligent assistant trained to classify documents into one of the following categories: "
                "'Lease', 'Contract', or 'Invoice'. You must strictly adhere to the definitions and instructions provided below."
            )
        },
        {
            "role": "user",
            "content": (
                "Based on the following document text, determine if it is a 'Lease', 'Contract', or 'Invoice'. "
                "Please classify the document according to the definitions and examples provided below:\n\n"
                "### Definitions:\n\n"
                "1. **Lease**:\n"
                "   - **Purpose**: A legally binding agreement specifically related to the rental of property or equipment.\n"
                "   - **Key Terms**: 'tenant', 'landlord', 'rent amount', 'lease period', 'security deposit', 'start date', 'end date', 'premises', 'maintenance', 'occupancy terms'.\n"
                "   - **Characteristics**: Includes detailed terms about the use of property, payment schedules, responsibilities for maintenance, and clauses about occupancy and termination specific to rental agreements.\n\n"
                "2. **Contract**:\n"
                "   - **Purpose**: A formal and legally binding agreement between two or more parties outlining mutual obligations, rights, and responsibilities.\n"
                "   - **Key Terms**: 'agreement', 'party', 'signatures', 'terms and conditions', 'obligations', 'deliverables', 'service terms'.\n"
                "   - **Characteristics**: Broad in scope and can pertain to various types of agreements such as service agreements, purchase agreements, employment contracts, etc. Unlike leases, contracts are not limited to property rentals and do not typically include rental-specific terms.\n\n"
                "3. **Invoice**:\n"
                "   - **Purpose**: A document issued by a seller to a buyer that specifies the products or services provided, along with the amount due.\n"
                "   - **Key Terms**: 'invoice number', 'amount due', 'due date', 'line items', 'description of goods or services', 'vendor information', 'payment terms'.\n"
                "   - **Characteristics**: Contains detailed billing information, including quantities, prices, and payment instructions. Primarily used for billing purposes.\n\n"
                "### Examples:\n\n"
                "**Lease Example**:\n\n"
                "This Housing Contract (“Contract”) is made and entered into as of 09/20/2023 (“Effective Date”) by and between Landlord and Resident, upon the terms and conditions stated below. ... [Lease-specific content]\n\n"
                "**Contract Example**:\n\n"
                "This Service Agreement (“Agreement”) is entered into on 01/01/2024 by and between ABC Services (“Provider”) and XYZ Company (“Client”). ... [Contract-specific content]\n\n"
                "**Invoice Example**:\n\n"
                "Invoice Number: 12345\nDate: 10/01/2023\nDue Date: 10/15/2023\nDescription: Web Design Services\nAmount Due: $2,000.00\n... [Invoice-specific content]\n\n"
                "### Instructions:\n\n"
                "1. **Classification Priority**: If the document is a specific type of contract, such as a lease, it should be classified as 'Lease' rather than the more general 'Contract'.\n"
                "2. **Response Format**: Please return your answer in JSON format as {'document_type': 'Lease'}, {'document_type': 'Contract'}, or {'document_type': 'Invoice'}.\n\n"
                "### Document Text to Analyze:\n\n"
                f"{text}"
            )
        }
        ]
        try:
            response = await self.client.chat.completions.create(
                messages=messages,
                model="gpt-4o-mini",
                temperature=0.0,
            )
            content = response.choices[0].message.content.strip()
            # Clean the response
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            # Parse JSON
            result = json.loads(content)
            document_type = result.get('document_type', '').lower()
            known_types = {'lease', 'contract', 'invoice'}
            if document_type in known_types:
                return document_type.capitalize()
            else:
                logger.warning(f"Unknown document type determined: {document_type}")
                return None
        except json.JSONDecodeError:
            logger.error("Error decoding JSON from OpenAI response.")
            return None
        except Exception as e:
            logger.error(f"An error occurred while determining document type: {e}")
            return None

    def _generate_prompt_by_type(self, text: str, document_type: str) -> list[ChatCompletionMessage]:
        """
        Generates a prompt based on the document type.  

        Args:
            text (str): The text extracted from the document.
            document_type (str): The type of the document (e.g., 'invoice', 'lease').

        Returns:
            list[ChatCompletionMessage]: The prompt formatted for OpenAI's ChatCompletion API.
        """
        # Generate the prompt based on document type
        if document_type.lower() == 'lease':
            return self._generate_lease_prompt(text)
        elif document_type.lower() == 'invoice':
            return self._generate_invoice_prompt(text)
        elif document_type.lower() == 'contract':
            return self._generate_contract_prompt(text)
        else:
            return self._generate_generic_prompt(text, document_type)

    def _generate_lease_prompt(self, text: str) -> list[ChatCompletionMessage]:
        """
        Generates a prompt for extracting key lease information in a specific JSON structure.
        """
        system_prompt = "You are an assistant that extracts lease information and formats it as JSON."
        user_prompt = (
            "Please extract the following details from the lease and return them in JSON format exactly as shown. "
            "If any information is missing, use 'Not Found' for that field. The 'Additional Fees' and 'Special Lease Terms' fields "
            "should include any relevant entries found in the document, not limited to specific examples.\n\n"
            "{"
            "  \"Lease Type\": \"Type of lease or contract\","
            "  \"Description\": \"High level, short description of document\","
            "  \"Property Information\": {"
            "    \"Address\": \"Complete property address\","
            "    \"Num Bedrooms\": null,  // Integer or null if not specified/commercial"
            "    \"Num Bathrooms\": null,  // Integer or null if not specified/commercial"
            "    \"Num Floors\": null,     // Integer or null if not specified"
            "    \"Is Commercial\": false,  // Boolean, true if commercial property"
            "    \"Property Type\": \"Type of property (e.g., apartment, house, office, retail)\""
            "  },"
            "  \"Rent Amount\": {"
            "    \"Total\": \"Total rent for the lease period\","
            "    \"Monthly Installment\": \"Monthly rent installment\""
            "  },"
            "  \"Security Deposit\": {"
            "    \"Amount\": \"Security deposit amount or 'Not Found' if absent\","
            "    \"Held By\": \"Entity holding the deposit or 'Not Found' if absent\""
            "  },"
            "  \"Start Date\": \"Start date of the lease MM/DD/YYYY\","
            "  \"End Date\": \"End date of the lease MM/DD/YYYY\","
            "  \"Tenant Information\": {"
            "    \"First Name\": \"First name of tenant\","
            "    \"Last Name\": \"Last name of tenant\","
            "    \"Landlord\": \"Name of landlord\","
            "    \"Address\": \"Tenant address\","
            "    \"Email\": \"Tenant email\","
            "    \"Phone Number\": \"Tenant phone number\","
            "    \"Date of Birth\": \"Tenant date of birth MM/DD/YYYY\","
            "    \"Status\": \"current\",\" late\", or \"previous\""
            "  },"            
            "  \"Payment Frequency\": \"Frequency of rent payments (e.g., Monthly, Quarterly)\","
            "  \"Special Lease Terms\": {"
            "    \"Late Payment\": {"
            "      \"Initial Fee\": \"Initial late payment fee or 'Not Found' if absent\","
            "      \"Daily Late Charge\": \"Daily charge for late payment or 'Not Found' if absent\""
            "    },"
            "    \"Additional Fees\": ["
            "      {\"Fee Type\": \"Type of fee, e.g., 'After-Hours Lockout'\", \"Amount\": \"Fee amount\"},"
            "      {\"Fee Type\": \"Type of fee, e.g., 'Animal Violation'\", \"First Violation\": \"Amount for first violation\", \"Additional Violation\": \"Amount for subsequent violations\"},"
            "      {\"Fee Type\": \"Type of fee, e.g., 'Contract Re-Assignment'\", \"Amount\": \"Fee amount\"},"
            "      {\"Fee Type\": \"Type of fee, e.g., 'Garbage Removal'\", \"Amount\": \"Fee amount and applicable rate, e.g., '$50.00 per item/bag per day'\"},"
            "      {\"Fee Type\": \"Type of fee, e.g., 'Holdover Resident'\", \"Amount\": \"Fee amount and applicable rate, e.g., '150% of Daily Rate per day'\"}"
            "    ]"
            "  }"
            "}\n\n"
            f"Text to analyze:\n\n{text}"
        )
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def _generate_invoice_prompt(self, text: str) -> list[ChatCompletionMessage]:
        """
        Generates a prompt for extracting key invoice information in a specific JSON structure.
        """
        system_prompt = "You are an assistant that extracts invoice information and formats it as JSON."
        user_prompt = (
            "Please extract the following details from the invoice and return them in JSON format exactly as shown. "
            "If any information is missing, use 'Not Found' for that field. For 'Line Items', list each item purchased with its details.\n\n"
            "{\n"
            "  \"Invoice Number\": \"Unique invoice number\",\n"
            "  \"Amount\": \"Total amount due\",\n"
            "  \"Paid Amount\": \"Amount already paid\",\n"
            "  \"Invoice Date\": \"Date of the invoice MM/DD/YYYY\",\n"
            "  \"Due Date\": \"Due date for payment MM/DD/YYYY\",\n"
            "  \"Status\": \"Status of the invoice (e.g., Unpaid, Paid)\",\n"
            "  \"Vendor Information\": {\n"
            "    \"Name\": \"Name of the vendor or supplier\",\n"
            "    \"Address\": \"Vendor address\"\n"
            "  },\n"
            "  \"Description\": \"Description of goods or services provided\",\n"
            "  \"Line Items\": [\n"
            "    {\n"
            "      \"Description\": \"Item description\",\n"
            "      \"Quantity\": \"Number of units\",\n"
            "      \"Unit Price\": \"Price per unit\",\n"
            "      \"Total Price\": \"Total price for this item\"\n"
            "    },\n"
            "    {\n"
            "      ...\n"
            "    }\n"
            "  ]\n"
            "}\n\n"
            f"Text to analyze:\n\n{text}"
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _generate_contract_prompt(self, text: str) -> list[ChatCompletionMessage]:
        """
        Generates a prompt for extracting key contract information in a specific JSON structure.
        """
        system_prompt = "You are an assistant that extracts contract information and formats it as JSON."
        user_prompt = (
            "Please extract the following details from the contract and return them in JSON format exactly as shown. "
            "If any information is missing, use 'Not Found' for that field. The 'Terms' field should include any relevant clauses found in the document, "
            "with each term represented as a key-value pair. The 'Parties Involved' should be a list of parties, "
            "with each party represented as an object containing their details.\n\n"
            "{\n"
            "  \"Contract Type\": \"Type of contract (e.g., Service Agreement, Maintenance Contract)\",\n"
            "  \"Description\": \"High-level, short description of the contract\",\n"
            "  \"Start Date\": \"Start date of the contract MM/DD/YYYY\",\n"
            "  \"End Date\": \"End date of the contract MM/DD/YYYY or 'Not Found' if indefinite\",\n"
            "  \"Parties Involved\": [\n"
            "    {\n"
            "      \"Name\": \"Name of the party\",\n"
            "      \"Address\": \"Party address\",\n"
            "      \"Contact Person\": \"Name of the contact person\",\n"
            "      \"Phone Number\": \"Contact phone number\",\n"
            "      \"Email\": \"Contact email address\",\n"
            "      \"Role\": \"Party's Role\"\n"
            "    },\n"
            "    { ... }\n"
            "  ],\n"
            "  \"Vendor Information\": {\n"
            "    \"Name\": \"Name of the vendor or service provider\",\n"
            "    \"Address\": \"Vendor address\",\n"
            "    \"Contact Person\": \"Name of the contact person at the vendor\",\n"
            "    \"Phone Number\": \"Contact phone number\",\n"
            "    \"Email\": \"Contact email address\"\n"
            "  },\n"
            "  \"Terms\": {\n"
            "    \"Payment Terms\": \"Details about payment schedules, amounts, and methods\",\n"
            "    \"Termination Clause\": \"Conditions under which the contract can be terminated\",\n"
            "    \"Confidentiality Clause\": \"Any confidentiality or non-disclosure agreements\",\n"
            "    \"Liability Clause\": \"Details about liability limitations\",\n"
            "    \"Dispute Resolution\": \"Methods for resolving disputes\",\n"
            "    \"Other Terms\": \"Any other significant terms and conditions\"\n"
            "  },\n"
            "  \"Is Active\": \"True if the contract is currently active, False otherwise\"\n"
            "}\n\n"
            f"Text to analyze:\n\n{text}"
        )
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _generate_generic_prompt(self, text: str, document_type: str) -> list[ChatCompletionMessage]:
        """
        Generates a generic prompt for unspecified document types.
        """
        system_prompt = f"You are an assistant that extracts information from {document_type}s."
        user_prompt = (
            f"Extract the relevant information from the following {document_type} "
            f"and provide it in JSON format:\n\n{text}"
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]