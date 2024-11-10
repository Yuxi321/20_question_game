"""Game manager module for managing the game flow."""
# pylint: disable-msg=C0301,R0903,W0718,W0511
# TODO: Catching too general exception
import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from agent import GameState, GuesserAgent, HostAgent, MultipleGuesserAgent


class BaseGameManager(ABC):
    """Base game manager to manager the game flow between host and guesser agents."""

    def __init__(self, host: HostAgent, max_questions: int = 20):
        self.host = host
        self.max_questions = max_questions
        self.game_state = GameState()

    @abstractmethod
    def setup_agent(self):
        """Abstract class for setting up guesser agent"""

    @abstractmethod
    def get_question(self):
        """Abstract class for getting next valid question"""

    def start_game(self) -> GameState:
        """Initialize a new game.

        Returns:
            GameState: The initial game state
        """
        print("Initialising agents playing 20 questions game")
        print("The host agent will think about a topic and guesser(s) will ask yes/no questions to guess")
        print("The host will then reply accordingly")
        print("As options narrow down, the guesser can make direct guesses.")
        print("If the guesser correctly guesses the topic, they win!")
        print("The guesser has up to 20 total questions and guesses to win")
        print("\n")
        self.game_state = GameState()
        self.game_state.topic = self.host.choose_topic()
        return self.game_state

    @abstractmethod
    def check_direct_guess(self, question: str) -> Optional[str]:
        """Check for direct guess"""
        # return guesser.validator.extract_guess(question)

    def play_turn(
        self,
    ) -> Tuple[GameState, str]:
        """Play one turn of the game.

        Returns:
            Tuple[GameState, str]: Updated game state and turn result message
        """
        if self.game_state.questions_asked >= self.max_questions:
            self.game_state.game_over = True
            self.game_state.winner = "host"
            return self.game_state, "Game Over - Host wins! Question number is over limit (20)."

        # # Get question from guesser
        # is_question_valid, msg = self.guesser.generate_question(self.game_state)
        #
        # while not is_question_valid:
        #     is_question_valid, msg = self.guesser.generate_question(self.game_state)
        # question = msg
        _, question = self.get_question()
        print(f"Guesser now making a new question: {question}")

        # Check if it's a direct guess
        direct_guess = self.check_direct_guess(question)

        # Get answer from host
        answer = self.host.answer_question(question, self.game_state.topic)
        print(f"Host anwsered this question: {answer}")

        # Update game state
        self.game_state.questions_asked += 1
        self.game_state.previous_questions.append(question)
        self.game_state.previous_answers.append(answer)

        # If it's a direct guess and correct, guesser wins and stop the game
        if direct_guess and answer and direct_guess.lower() == self.game_state.topic.lower():
            self.game_state.game_over = True
            self.game_state.winner = "guesser"
            return self.game_state, f"Game Over - Guesser wins! The topic was {self.game_state.topic}"

        return (self.game_state, f"Q: {question}\nA: {'Yes' if answer else 'No'}")


class SingleGameManager(BaseGameManager):
    """
    Game manager managing the game flow with single agent
    """

    def __init__(self, host: HostAgent, guesser: GuesserAgent, max_questions: int = 20):
        super().__init__(host, max_questions)
        self.guesser = guesser

    def setup_agent(self):
        pass

    def get_question(self) -> Tuple[bool, str]:
        is_valid, msg = self.guesser.generate_question(self.game_state)
        while not is_valid:
            is_valid, msg = self.guesser.generate_question(self.game_state)
        question = msg
        return True, question

    def check_direct_guess(self, question: str) -> Optional[str]:
        return self.guesser.validator.extract_guess(question)


class MultipleAgentGameManager(BaseGameManager):
    """
    Game manager managing the game flow with multiple sub agents
    """

    def __init__(self, host: HostAgent, guessers: List[MultipleGuesserAgent], max_questions: int = 20):
        super().__init__(host, max_questions)
        self.guessers = guessers

    def setup_agent(self):
        pass

    def get_question(self) -> Tuple[bool, str]:
        """Synchronous wrapper for async question generation"""
        return asyncio.run(self._get_question())

    async def _get_question(self) -> Tuple[bool, str]:
        """Get first valid question from competing agents"""
        tasks = [agent.generate_question_async(self.game_state) for agent in self.guessers]

        try:
            # Wait for all tasks to complete or first valid question
            while tasks:
                done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

                # Process completed tasks in order of completion
                for task in done:
                    is_valid, result = task.result()
                    if is_valid:
                        # Once the first one got complete, cancel remaining tasks
                        for remaining_task in tasks:
                            remaining_task.cancel()
                        return True, result

                # Update remaining tasks
                tasks = set(remaining_task for remaining_task in tasks if not remaining_task.done())

            return False, "No valid question generated"

        except Exception as exception:
            print(f"Error in question generation: {str(exception)}")
            return False, "Error in question generation"

    def check_direct_guess(self, question: str) -> Optional[str]:
        """Check for direct guess - using first guesser's validator"""
        return self.guessers[0].validator.extract_guess(question)
