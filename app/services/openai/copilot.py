# app/services/openai/copilot.py

import logging
import json
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessage
from app.core.config import settings

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class OpenAIService:
    def __init__(self):
        # Initialize the OpenAI client with your API key
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def parse_intent_and_entities(self, message: str) -> dict:
        """
        Uses OpenAI's API to parse the user's message and extract intent and entities.

        Args:
            message (str): The user's message.

        Returns:
            dict: A dictionary containing 'intent' and 'entities'.
        """
        messages = self._generate_prompt(message)

        try:
            # Make an asynchronous request to OpenAI with the chat completion API
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  
                messages=messages,
                temperature=0.0,
            )

            # Extract content and remove any ```json markers
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:]  # Remove the starting ```json
            if content.endswith("```"):
                content = content[:-3]  # Remove the ending ```

            # Now attempt to parse the cleaned JSON string
            parsed_data = json.loads(content)
            return parsed_data

        except json.JSONDecodeError:
            logger.error("Error decoding JSON from OpenAI response.")
            return {}
        except Exception as e:
            logger.error(f"An error occurred while parsing intent and entities: {e}")
            return {}

    def _generate_prompt(self, message: str) -> list:
        """
        Generates a prompt instructing OpenAI to parse the user's message into intent and entities.

        Args:
            message (str): The user's message.

        Returns:
            list: The prompt formatted for OpenAI's Chat Completion API.
        """
        system_prompt = "You are an assistant that helps parse user messages into intents and entities for a property management application."
        user_prompt = (
            "Please identify the intent and any entities in the following user message. "
            "Return the result in **valid JSON format** like this:\n"
            "```\n"
            "{\n"
            '  "intent": "intent_name",\n'
            '  "entities": {\n'
            '    "entity_name": "entity_value",\n'
            '    ...\n'
            '  }\n'
            '}\n'
            "```\n"
            "Possible intents are:\n"
            "- get_highest_expense_by_property\n"
            "- get_highest_expense_across_properties\n"
            "- list_properties\n"
            "Possible entities are:\n"
            "- property_name\n"
            "- property_id\n"
            "\nUser message:\n"
            f"{message}"
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
