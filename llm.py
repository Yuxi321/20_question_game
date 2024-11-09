"""Module for handling LLM (Large Language Model) interactions via the Anthropic API."""
# pylint: disable-msg=C0301,R0903
from typing import Optional

from anthropic import Anthropic, APIError, RateLimitError  # pylint: disable=import-error


class LLMError(Exception):
    """Custom exception for LLM-related errors."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error


class LLMInterface:
    """Interface for interacting with the Anthropic Claude API."""

    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        """Initialize the LLM interface.

        Args:
            api_key: Anthropic API key for authentication
            model: Model identifier to use for generation
        """
        self.api_key = api_key
        self.max_tokens = 1024
        self.llm_client = Anthropic(
            api_key=api_key,
        )
        self.model = model

    def generate_response(self, prompt: str) -> str:
        """Interact with Claude API to generate response.

        Args:
            prompt: The input prompt for the LLM

        Returns:
            The LLM's response text

        Raises:
            LLMError: When any error occurs during LLM interaction
        """
        try:
            message = self.llm_client.messages.create(
                max_tokens=self.max_tokens, messages=[{"role": "user", "content": prompt}], model=self.model
            )
            return message.content[0].text

        except APIError as api_error:
            raise LLMError(f"API Error: {str(api_error)}", api_error) from api_error

        except RateLimitError as rate_error:
            raise LLMError(f"Rate Limit Exceeded: {str(rate_error)}", rate_error) from rate_error

        except Exception as unknown_error:
            raise LLMError(
                f"Unexpected error during LLM call: {str(unknown_error)}", unknown_error
            ) from unknown_error
