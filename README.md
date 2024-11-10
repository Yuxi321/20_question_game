
# 20 Questions Game with AI Agents

An implementation of the classic 20 Questions game using AI agents. The game uses Claude API to generate questions and answers between AI agents.

## Setup

### Prerequisites
- Python 3.8 or higher
- Anthropic API key

### Installation

1. Clone the repository
```bash
git clone https://github.com/Yuxi321/20_question_game.git
```

2. Install dependencies
```bash
pip install -r requirements.txt
```
3. Create a config.json file in the root directory:
```bash
{
    "api_key": "your-anthropic-api-key",
    "game_mode": "single",  # or "multi" for multiple agents
    "num_agents": 5,        # only used if game_mode is "multi"
    "max_questions": 20
}
```

### Running the Game
To start the game:
```bash
python main.py
```

### Game Rules
* A host agent selects a topic
* Guesser agent(s) ask yes/no questions to identify the topic
* Maximum 20 questions allowed per game
* Game ends when:
  * A guesser correctly identifies the topic
  * All 20 questions are used without a correct guess

A guesser correctly identifies the topic
All 20 questions are used without a correct guess


### Game Mode
Single Player Mode
* One AI agent asks questions sequentially
* Set "game_mode": "single" in config.json

Multi Player Mode
* Multiple AI agents compete to ask questions
* First valid question from the most competitive agenet gets to be asked
* All agents share the same game state
* Set "game_mode": "multi" and specify "num_agents" in config.json

Output Files
* game_error_logs.json: Contains validation errors and game events
* result_and_logs.json: Contains game results and question history
