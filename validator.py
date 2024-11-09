"""Module for validating questions, including similarity checks and guess extraction."""
# pylint: disable-msg=C0301,W1404
import re
from typing import List, Optional, Tuple

from game_state import GameState, LogType


class QuestionValidator:
    """Validates questions for the 20 questions game, including format and similarity checks."""

    def __init__(self, similarity_threshold: float = 0.5):
        # Common patterns that aren't yes/no questions
        self.invalid_patterns = [
            r"^what",
            r"^how",
            r"^who",
            r"^where",
            r"^when",
            r"^why",
            r"^which",
            r"^can you tell",
            r"^tell me",
        ]
        self.similarity_threshold = similarity_threshold

        # Patterns to identify direct guesses
        self.direct_guess_patterns = [
            r"^is it (?:a |an |the )?([a-zA-Z0-9\s-]+)\??$",
            r"^could it be (?:a |an |the )?([a-zA-Z0-9\s-]+)\??$",
            r"^would it be (?:a |an |the )?([a-zA-Z0-9\s-]+)\??$",
            r"^are you thinking of (?:a |an |the )?([a-zA-Z0-9\s-]+)" r"\??$",
            r"^is the answer (?:a |an |the )?([a-zA-Z0-9\s-]+)\??$",
            # Simple pattern for "umbrella?" or "elephant?"
            r"^([a-zA-Z0-9\s-]+)\??$",
        ]

    def is_valid_question(self, question: str, game_state: GameState) -> Tuple[bool, Optional[str]]:
        """Validate if the question is properly formatted as a yes/no question.

        Args:
            question: The question to validate
            game_state: Current game state for logging

        Returns:
            Tuple of (is_valid, error_message)
        """
        question = question.lower().strip()

        # Check if empty
        if not question:
            error_msg = "Question could not be empty. Please give a valid question"
            game_state.add_error_log(LogType.VALIDATION_ERROR, error_msg, question=question)
            return False, error_msg

        # Check if it contains invalid question words
        for pattern in self.invalid_patterns:
            if re.search(pattern, question):
                error_msg = f"Question starts with '{pattern}', " "it's mostly not a valid question"
                game_state.add_error_log(
                    LogType.VALIDATION_ERROR, error_msg, question=question, details={"pattern": pattern}
                )
                return False, error_msg
        return True, None

    def is_similar_to_previous(
        self, question: str, previous_questions: List[str], game_state: GameState
    ) -> Tuple[bool, str]:
        """Check if question is too similar to previous questions.

        Args:
            question: The question to check
            previous_questions: List of previously asked questions
            game_state: Current game state for logging

        Returns:
            Tuple of (is_similar, error_message)
        """
        question = question.lower().strip()

        for prev in previous_questions:
            prev = prev.lower().strip()
            # Exact match check
            if question == prev:
                error_msg = "Question is exact same with one of the previous one"
                game_state.add_error_log(
                    LogType.SIMILARITY_ERROR, error_msg, question=question, details={"matched_with": prev}
                )
                return True, error_msg

        return False, None

    def extract_guess(self, question: str) -> Optional[str]:
        """Extract the guess from a question if it's a direct guess.

        Args:
            question: The question to extract a guess from

        Returns:
            The extracted guess if found, None otherwise
        """
        question = question.lower().strip()

        for pattern in self.direct_guess_patterns:
            match = re.match(pattern, question)
            if match:
                return match.group(1).strip()
        return None
