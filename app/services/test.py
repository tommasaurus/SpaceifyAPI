import asyncio
import sys
import os
from io import BytesIO
import json
import logging

# Project imports
project_root = '/Users/tommyqu/Desktop/CS/AiPropertyDevelopment'
sys.path.append(project_root)
from app.services.document_processor import extract_text_from_file
from app.services.openai.openai_document import OpenAIService
from app.services.mapping_functions import parse_json, map_lease_data, map_invoice_data

# Initialize logger
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

# TESTING FOR LEASES
# async def main():
#     # Define the file path and filename
#     file_path = "/Users/tommyqu/Downloads/signed_packet_file_lease_document_13319627_1695223376.pdf"
#     filename = "signed_packet_file_lease_document_13319627_1695223376.pdf"

#     # Open the file in binary mode and wrap it in a BytesIO object
#     with open(file_path, "rb") as f:
#         file_like = BytesIO(f.read())

#     # Extract text from the file
#     text = extract_text_from_file(file_like, filename)

#     if text:        
#         # Initialize OpenAIService
#         openai_service = OpenAIService()

#         # Extract structured information
#         document_type = "lease"
#         extracted_data = await openai_service.extract_information(text, document_type)

#         if extracted_data:
#             print("\nExtracted Information:")
#             print(json.dumps(extracted_data, indent=4))

#             # Step 1: Parse the JSON to ensure consistency
#             parsed_data = parse_json(json.dumps(extracted_data))
#             print("\nParsed Data:")
#             print(json.dumps(parsed_data, indent=4))

#             # Step 2: Map to Lease model fields
#             mapped_data = map_lease_data(parsed_data)
#             print("\nMapped Data for Lease Model:")
#             print(json.dumps(mapped_data, indent=4))
#         else:
#             print("No structured information could be extracted from the lease.")
#     else:
#         print("No text could be extracted from the file.")


# TESTING FOR INVOICES
async def main():
    # Define the file path and filename
    file_path = "/Users/tommyqu/Downloads/receipt1.jpeg"
    filename = "receipt1.jpeg"

    # Open the file in binary mode and wrap it in a BytesIO object
    with open(file_path, "rb") as f:
        file_like = BytesIO(f.read())

    # Extract text from the file
    text = extract_text_from_file(file_like, filename)
    
    if text:        
        # Initialize OpenAIService
        openai_service = OpenAIService()

        # Extract structured information
        document_type = "invoice"
        extracted_data = await openai_service.extract_information(text, document_type)

        if extracted_data:
            print("\nExtracted Information:")
            print(json.dumps(extracted_data, indent=4))

            # Step 1: Parse the JSON to ensure consistency
            parsed_data = parse_json(json.dumps(extracted_data))
            print("\nParsed Data:")
            print(json.dumps(parsed_data, indent=4))

            # Step 2: Map to invoice model fields
            mapped_data = map_invoice_data(parsed_data)
            print("\nMapped Data for Invoice Model:")
            print(json.dumps(mapped_data, indent=4))
        else:
            print("No structured information could be extracted from the invoice.")
    else:
        print("No text could be extracted from the file.")

# Run the asynchronous main function
if __name__ == "__main__":
    asyncio.run(main())
