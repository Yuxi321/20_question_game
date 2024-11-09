"""Module containing agent implementations for the 20 questions game."""
# pylint: disable-msg=C0301,R0903,W0718
from typing import Tuple

from game_state import GameState
from llm import LLMInterface
from validator import QuestionValidator


class BaseAgent:
    """Base class for game agents providing common functionality."""

    def __init__(self, name: str, role: str, llm: LLMInterface = None):
        self.name = name
        self.role = role  # 'host' or 'guesser'
        self.llm = llm

    def get_context(self, game_state: GameState) -> str:
        """Generate context string based on game history"""
        context = "Previous questions and answers:\n"
        for question, answer in zip(game_state.previous_questions, game_state.previous_answers):
            context += f"Q: {question}\nA: {'Yes' if answer else 'No'}\n"
        return context


class HostAgent(BaseAgent):
    """Agent implementation for the host role in 20 questions game."""

    def choose_topic(self) -> str:
        """Use LLM to generate a random topic"""
        return "Quantum supercomputer"

    def answer_question(self, question: str, topic: str) -> bool:
        """Generate yes/no answer using LLM"""
        answer_prompt = f"""
        You are hosting a 20 questions game. The secret topic is '{topic}'.
        User is asking the following question:
        Question: {question}
        Do you think the question is related to this topic?
        You are only expected to answer with just 'yes' or 'no', nothing else.

        Example usage:
        The secret topic is 'apple'

        Q: Is this an item?
        A: yes

        Q: Is this science related?
        A: no

        Q: Is a food?
        A: yes
        """

        try:
            answer = self.llm.generate_response(answer_prompt)
            return answer == "yes"
        except Exception:
            return False


class GuesserAgent(BaseAgent):
    """Agent implementation for the guesser role in 20 questions game."""

    def __init__(self, name: str, role: str, llm: LLMInterface):
        super().__init__(name, role, llm)
        self.validator = QuestionValidator()

    def generate_question(self, game_state: GameState) -> Tuple[bool, str]:
        """Generate next question based on game history with validation"""
        question_prompt = f"""
            You are playing 20 questions. Generate the next yes/no question based on previous Q&A:

            Rules:
            1. Question must be answerable with yes/no only
            2. Preassumably start with: is/does/can/will/has/are/would/could/should
            3. Please don't ask similar questions to waste your chance

            Narrow down the question based on previous Q&A

            Questions asked so far: {game_state.questions_asked}/20.
            Previous Q&A: {self.get_context(game_state)}

            Now giving your question based on the previous Q&As and approaching to the correct answer.
            Only the question, no need to give out explaination
        """

        try:
            question = self.llm.generate_response(question_prompt)
            # Validate question format
            is_valid, error_msg = self.validator.is_valid_question(question=question, game_state=game_state)
            if not is_valid:
                return False, error_msg

            # Check for similarity with previous questions
            is_repeated_question, error_msg = self.validator.is_similar_to_previous(
                question=question, previous_questions=game_state.previous_questions, game_state=game_state
            )
            if is_repeated_question:
                return False, error_msg

            return True, question
        except Exception:
            return False, "Problem interacting with llm"
