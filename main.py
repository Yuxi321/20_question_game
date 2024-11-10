"""Main module for running the 20 questions game with LLM-powered agents."""
# pylint: disable-msg=C0301,R0903
import json

# from agent import GameState, GuesserAgent, HostAgent
from agent import GuesserAgent, HostAgent, MultipleGuesserAgent
from game_manager import MultipleAgentGameManager, SingleGameManager
from llm import LLMInterface


def play_game(host_name: str = "IntelligenceBot") -> dict:
    """Play a complete game and return the results.

    Args:
        host_name: Name for the host agent
        guesser_name: Name for the guesser agent

    Returns:
        dict: Game results including winner, topic, questions asked, and game log
    """
    with open("config.json", encoding="utf-8") as config_file:
        config = json.load(config_file)

    # set up llm manager
    api_key = config["api_key"]
    llm = LLMInterface(api_key=api_key)

    # set up host agent
    host = HostAgent(name=host_name, role="host", llm=llm)

    # set up guesser agent(s) and corresponding game manager
    if config["game_mode"] == "single":
        guesser = GuesserAgent(name="Test Guesser", role="guesser", llm=llm)
        game_manager = SingleGameManager(host, guesser)
    else:
        guessers = [MultipleGuesserAgent(f"Player_{i}", "guesser", llm) for i in range(config["num_agents"])]
        game_manager = MultipleAgentGameManager(host, guessers)

    game_manager.start_game()
    game_log = []

    while not game_manager.game_state.game_over:
        _, message = game_manager.play_turn()
        game_log.append(message)

    game_manager.game_state.export_logs("output/game_error_logs.json")

    result_and_logs = {
        "winner": game_manager.game_state.winner,
        "topic": game_manager.game_state.topic,
        "questions_asked": game_manager.game_state.questions_asked,
        "game_log": game_log,
    }

    with open("output/result_and_logs.json", "w", encoding="utf-8") as log_file:
        json.dump(result_and_logs, log_file, indent=2)

    return result_and_logs


if __name__ == "__main__":
    play_game()
