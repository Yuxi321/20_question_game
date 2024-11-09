"""Module containing game state and logging implementations"""
# pylint: disable-msg=C0301
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class LogType(Enum):
    """Enumeration of different types of game logs."""

    VALIDATION_ERROR = "validation_error"
    SIMILARITY_ERROR = "similarity_error"
    GAME_EVENT = "game_event"
    QUESTION = "question"
    ANSWER = "answer"


@dataclass
class GameLog:
    """Data class representing a single game log entry."""

    timestamp: str
    log_type: LogType
    message: str
    question: Optional[str] = None
    details: Optional[Dict] = None


class GameState:
    """Class representing the current state of a 20 questions game."""

    questions_asked: int = 0
    topic: str
    previous_questions: List[str] = []
    previous_answers: List[bool] = []
    game_over: bool = False
    winner: Optional[str] = None
    error_logs: List[GameLog] = []

    def __post_init__(self):
        if self.previous_questions is None:
            self.previous_questions = []
        if self.previous_answers is None:
            self.previous_answers = []

    def add_error_log(
        self, log_type: LogType, message: str, question: Optional[str] = None, details: Optional[Dict] = None
    ):
        """Add a log entry to the game state.

        Args:
            log_type: Type of the log entry from LogType enum
            message: Description of the log event
            question: Optional question that triggered the log
            details: Optional additional details about the log event
        """
        log = GameLog(
            timestamp=datetime.now().isoformat(),
            log_type=log_type,
            message=message,
            question=question,
            details=details,
        )
        self.error_logs.append(log)

    def export_logs(self, filepath: str):
        """Export error logs to a JSON file.

        Args:
            filepath: Path where the JSON file should be saved
        """
        logs_dict = [
            {
                "timestamp": log.timestamp,
                "type": log.log_type.value,
                "message": log.message,
                "question": log.question,
                "details": log.details,
            }
            for log in self.error_logs
        ]

        with open(filepath, "w", encoding="utf-8") as file_handle:
            json.dump(logs_dict, file_handle, indent=2)
