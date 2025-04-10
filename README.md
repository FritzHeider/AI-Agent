# AI Agent System

A general AI agent that can automatically send commands to the computer terminal and interact with websites and applications.

## Overview

This AI Agent system combines terminal control, web interaction, and AI decision-making capabilities to create a versatile automation tool. The agent can:

- Execute terminal commands and process their outputs
- Navigate and interact with websites using browser automation
- Make intelligent decisions using AI to accomplish complex tasks
- Process natural language instructions from users
- Execute multi-step plans to achieve goals

## Components

The system consists of several key components:

1. **Terminal Control Module** - Provides functionality for executing shell commands, parsing command outputs, and handling errors in terminal operations.

2. **Web Interaction Module** - Enables browser automation, web navigation, element interaction, and content extraction using Selenium.

3. **AI Decision-Making Component** - Powers the agent's intelligence using OpenAI's API for generating responses, commands, and plans.

4. **Integration Module** - Combines all components into a cohesive system with context management and task execution.

5. **Command-Line Interface** - Provides a user-friendly way to interact with the agent through natural language or direct commands.

## Installation

### Prerequisites

- Python 3.10 or higher
- Chrome browser (for web interaction)
- Internet connection
- OpenAI API key (for AI capabilities)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-agent.git
   cd ai-agent
   ```

2. Install required packages:
   ```bash
   pip install selenium beautifulsoup4 openai langchain webdriver-manager python-dotenv
   ```

3. Create a `.env` file with your OpenAI API key:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file to add your OpenAI API key.

## Usage

### Basic Usage

Run the command-line interface:

```bash
python cli.py
```

This will start an interactive session where you can type instructions or commands.

### Command Examples

In the interactive CLI, you can:

- Type natural language instructions:
  ```
  Find information about the weather in New York
  ```

- Execute terminal commands directly:
  ```
  execute ls -la
  ```

- Navigate to websites:
  ```
  browse https://example.com
  ```

- Generate and execute plans:
  ```
  plan Create a simple HTML page and open it in the browser
  ```

- Get help:
  ```
  help
  ```

- Check agent status:
  ```
  status
  ```

- View command history:
  ```
  history
  ```

- Exit the program:
  ```
  exit
  ```

### Command-Line Arguments

The CLI supports several command-line arguments:

```bash
python cli.py --help
```

Options include:
- `--api-key KEY` - Specify OpenAI API key
- `--visible-browser` - Run browser in visible mode (not headless)
- `--command CMD` - Run a single command and exit
- `--execute CMD` - Execute a terminal command and exit
- `--browse URL` - Navigate to a URL and exit
- `--plan GOAL` - Execute a plan for a goal and exit

## Architecture

The system follows a modular architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Terminal       │     │  Web            │     │  AI Decision    │
│  Control Module │     │  Interaction    │     │  Making         │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────┬───────┴───────────────┬───────┘
                         │                       │
                ┌────────┴────────┐     ┌────────┴────────┐
                │  AI Agent       │     │  Command-Line   │
                │  Integration    │     │  Interface      │
                └─────────────────┘     └─────────────────┘
```

## Extending the Agent

### Adding New Capabilities

To add new capabilities to the agent:

1. Create a new module in a separate Python file
2. Import and integrate it in the `ai_agent.py` file
3. Add methods to expose the functionality
4. Update the CLI to provide access to the new features

### Customizing AI Behavior

You can customize the AI behavior by:

1. Modifying the system prompt in `ai_decision.py`
2. Adjusting the temperature parameter for more/less creative responses
3. Implementing custom parsing logic for specific types of tasks

## Troubleshooting

### Common Issues

- **Browser automation issues**: Make sure Chrome is installed and up to date
- **API key errors**: Check that your OpenAI API key is correctly set in the `.env` file
- **Permission errors**: Ensure you have the necessary permissions to execute commands
- **Timeout errors**: For long-running operations, consider increasing timeout values in the code

### Logs

The system creates log files that can help diagnose issues:
- `ai_agent.log` - General agent logs
- `test_scenarios.log` - Test logs

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for the AI capabilities
- Selenium for web automation
- The open-source community for various libraries used in this project
# AI-Agent
