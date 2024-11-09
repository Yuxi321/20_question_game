"""Main module for running the 20 questions game with LLM-powered agents."""
# pylint: disable-msg=C0301,R0903
import json
from typing import Tuple

from agent import GameState, GuesserAgent, HostAgent
from llm import LLMInterface


class GameManager:
    """Manages the game flow between host and guesser agents."""

    def __init__(self, host: HostAgent, guesser: GuesserAgent, max_questions: int = 20):
        self.host = host
        self.guesser = guesser
        self.max_questions = max_questions
        self.game_state = GameState()

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

    def play_turn(self) -> Tuple[GameState, str]:
        """Play one turn of the game.

        Returns:
            Tuple[GameState, str]: Updated game state and turn result message
        """
        if self.game_state.questions_asked >= self.max_questions:
            self.game_state.game_over = True
            self.game_state.winner = "host"
            return self.game_state, "Game Over - Host wins! Question number is over limit (20)."

        # Get question from guesser
        is_question_valid, msg = self.guesser.generate_question(self.game_state)

        while not is_question_valid:
            is_question_valid, msg = self.guesser.generate_question(self.game_state)
        question = msg
        print(f"Guesser now making a new question: {question}")

        # Check if it's a direct guess
        guess = self.guesser.validator.extract_guess(question)

        # Get answer from host
        answer = self.host.answer_question(question, self.game_state.topic)
        print(f"Host anwsered this question: {answer}")

        # Update game state
        self.game_state.questions_asked += 1
        self.game_state.previous_questions.append(question)
        self.game_state.previous_answers.append(answer)

        # If it's a direct guess and correct, guesser wins and stop the game
        if guess and answer and guess.lower() == self.game_state.topic.lower():
            self.game_state.game_over = True
            self.game_state.winner = "guesser"
            return self.game_state, f"Game Over - Guesser wins! The topic was {self.game_state.topic}"

        return (self.game_state, f"Q: {question}\nA: {'Yes' if answer else 'No'}")


def play_game(host_name: str = "IntelligenceBot", guesser_name: str = "Player") -> dict:
    """Play a complete game and return the results.

    Args:
        host_name: Name for the host agent
        guesser_name: Name for the guesser agent

    Returns:
        dict: Game results including winner, topic, questions asked, and game log
    """
    with open("config.json", encoding="utf-8") as config_file:
        config = json.load(config_file)
    api_key = config["api_key"]
    llm = LLMInterface(api_key=api_key)

    host = HostAgent(name=host_name, role="host", llm=llm)
    guesser = GuesserAgent(name=guesser_name, role="guesser", llm=llm)
    game = GameManager(host, guesser)

    game.start_game()
    game_log = []

    while not game.game_state.game_over:
        _, message = game.play_turn()
        game_log.append(message)

    game.game_state.export_logs("output/game_error_logs.json")

    result_and_logs = {
        "winner": game.game_state.winner,
        "topic": game.game_state.topic,
        "questions_asked": game.game_state.questions_asked,
        "game_log": game_log,
    }

    with open("output/result_and_logs.json", "w", encoding="utf-8") as log_file:
        json.dump(result_and_logs, log_file, indent=2)

    return result_and_logs


if __name__ == "__main__":
    play_game()
