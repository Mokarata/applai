from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel

# Define a TypeVar for the Pydantic model, ensuring it's a BaseModel subclass
T_BaseModel = TypeVar('T_BaseModel', bound=BaseModel)

class LLMServiceProtocol(ABC):
    """
    Protocol defining the interface for LLM services.
    Ensures that all LLM services implement a consistent method
    for generating structured outputs.
    """

    @abstractmethod 
    async def generate_text_from_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        input_vars: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Asynchronously generates plain text from the LLM based on a system prompt and a user prompt.

        Args:
            system_prompt: The system prompt template.
            user_prompt: The user prompt template.
            input_vars: Dictionary of variables for prompt templates.

        Returns:
            A string containing the LLM's response.

        Raises:
            Exception: If the LLM fails to generate output.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod    
    async def generate_structured_output(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: Type[T_BaseModel],
        input_vars: Optional[Dict[str, Any]] = None,
    ) -> T_BaseModel:
        """
        Asynchronously generates structured output from the LLM based on a Pydantic model.

        Args:
            output_schema: The Pydantic model class to structure the LLM's output.
            system_prompt: The system prompt template.
            user_prompt: The user prompt template.
            input_vars: Dictionary of variables for prompt templates.

        Returns:
            An instance of the output_schema populated with the LLM's response.

        Raises:
            Exception: If the LLM fails to generate output or if the output
                       cannot be parsed into the specified schema.
        """
        raise NotImplementedError("Subclasses must implement this method.")
