#!/usr/bin/env python3
"""
AI Agent System - Command Line Interface

This module provides a user-friendly command-line interface
for interacting with the AI Agent system.
"""

import os
import sys
import argparse
import logging
import json
import readline
import signal
import time
from typing import Dict, List, Optional, Any

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the AI Agent
from ai_agent import AIAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ai_agent_cli')

class AIAgentCLI:
    """
    Command-line interface for the AI Agent system.
    """
    
    def __init__(self, api_key: Optional[str] = None, headless: bool = True):
        """
        Initialize the CLI with an AI Agent.
        
        Args:
            api_key: OpenAI API key. If None, tries to get from environment variable.
            headless: Whether to run the browser in headless mode.
        """
        self.api_key = api_key
        self.headless = headless
        self.agent = None
        self.running = False
        self.history = []
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_terminate)
        
        logger.info("AI Agent CLI initialized")
    
    def _handle_interrupt(self, sig, frame):
        """
        Handle keyboard interrupt (Ctrl+C).
        """
        print("\nInterrupted by user. Type 'exit' to quit or press Enter to continue.")
    
    def _handle_terminate(self, sig, frame):
        """
        Handle termination signal.
        """
        print("\nTermination signal received. Shutting down...")
        self.shutdown()
        sys.exit(0)
    
    def initialize_agent(self):
        """
        Initialize the AI Agent.
        """
        try:
            print("Initializing AI Agent...")
            self.agent = AIAgent(api_key=self.api_key, headless=self.headless)
            print("AI Agent initialized successfully!")
            return True
        except Exception as e:
            logger.error(f"Error initializing AI Agent: {str(e)}")
            print(f"Error initializing AI Agent: {str(e)}")
            return False
    
    def shutdown(self):
        """
        Shutdown the AI Agent and clean up resources.
        """
        if self.agent:
            try:
                print("Shutting down AI Agent...")
                self.agent.close()
                print("AI Agent shut down successfully!")
            except Exception as e:
                logger.error(f"Error shutting down AI Agent: {str(e)}")
                print(f"Error shutting down AI Agent: {str(e)}")
        
        self.running = False
    
    def process_command(self, command: str) -> bool:
        """
        Process a CLI command.
        
        Args:
            command: The command to process.
            
        Returns:
            True to continue, False to exit.
        """
        command = command.strip()
        
        # Add to history
        if command and command not in ["exit", "quit"]:
            self.history.append(command)
        
        # Process special commands
        if not command:
            return True
        
        if command.lower() in ["exit", "quit"]:
            self.shutdown()
            return False
        
        if command.lower() == "help":
            self._show_help()
            return True
        
        if command.lower() == "status":
            self._show_status()
            return True
        
        if command.lower() == "history":
            self._show_history()
            return True
        
        if command.lower().startswith("execute "):
            # Direct terminal command execution
            terminal_command = command[8:].strip()
            self._execute_terminal_command(terminal_command)
            return True
        
        if command.lower().startswith("browse "):
            # Direct browser navigation
            url = command[7:].strip()
            self._execute_browser_action("navigate", url=url)
            return True
        
        if command.lower().startswith("plan "):
            # Execute a plan for a goal
            goal = command[5:].strip()
            self._execute_plan(goal)
            return True
        
        # Default: process as a user request
        self._process_user_request(command)
        return True
    
    def _show_help(self):
        """
        Show help information.
        """
        print("\nAI Agent CLI Help:")
        print("------------------")
        print("Commands:")
        print("  help                  - Show this help information")
        print("  status                - Show agent status")
        print("  history               - Show command history")
        print("  execute <command>     - Execute a terminal command directly")
        print("  browse <url>          - Navigate to a URL directly")
        print("  plan <goal>           - Generate and execute a plan for a goal")
        print("  exit, quit            - Exit the program")
        print("\nGeneral Usage:")
        print("  Type any instruction or question to interact with the AI Agent")
        print("  The agent will process your request and take appropriate actions")
        print("  Use Ctrl+C to interrupt long-running operations")
        print()
    
    def _show_status(self):
        """
        Show agent status.
        """
        if not self.agent:
            print("\nAgent Status: Not initialized")
            return
        
        print("\nAgent Status:")
        print("-------------")
        print(f"Running: {self.running}")
        
        # Get context information
        self.agent.update_context()
        context = self.agent.current_context
        
        print(f"Current Directory: {context.get('terminal_dir', 'Unknown')}")
        print(f"Browser URL: {context.get('browser_url', 'Not browsing')}")
        print(f"Browser Title: {context.get('browser_title', '')}")
        
        # Show last command if available
        if context.get('last_command'):
            print(f"\nLast Command: {context['last_command']}")
        
        print()
    
    def _show_history(self):
        """
        Show command history.
        """
        print("\nCommand History:")
        print("----------------")
        if not self.history:
            print("No commands in history")
        else:
            for i, cmd in enumerate(self.history, 1):
                print(f"{i}. {cmd}")
        print()
    
    def _execute_terminal_command(self, command: str):
        """
        Execute a terminal command directly.
        """
        if not self.agent:
            print("Error: Agent not initialized")
            return
        
        print(f"\nExecuting: {command}")
        result = self.agent.execute_terminal_command(command)
        
        print(f"Status: {'Success' if result['status'] == 0 else 'Failed'}")
        if result['stdout']:
            print("\nOutput:")
            print(result['stdout'])
        if result['stderr'] and result['status'] != 0:
            print("\nError:")
            print(result['stderr'])
        print()
    
    def _execute_browser_action(self, action: str, **kwargs):
        """
        Execute a browser action directly.
        """
        if not self.agent:
            print("Error: Agent not initialized")
            return
        
        print(f"\nExecuting browser action: {action}")
        result = self.agent.execute_browser_action(action, **kwargs)
        
        print(f"Result: {result['message']}")
        if 'content' in result:
            print("\nContent:")
            if isinstance(result['content'], str):
                print(result['content'][:500] + ("..." if len(result['content']) > 500 else ""))
            else:
                print(json.dumps(result['content'], indent=2))
        print()
    
    def _execute_plan(self, goal: str):
        """
        Generate and execute a plan for a goal.
        """
        if not self.agent:
            print("Error: Agent not initialized")
            return
        
        print(f"\nGenerating and executing plan for: {goal}")
        print("This may take some time...")
        
        try:
            result = self.agent.execute_plan(goal)
            
            print("\nPlan Execution Results:")
            print("----------------------")
            
            # Display the plan
            print("\nPlan:")
            for step in result['plan']:
                print(f"{step.get('step', '?')}. {step.get('action', 'Action')}: {step.get('description', '')}")
            
            # Display results
            print("\nExecution Results:")
            for i, step_result in enumerate(result['results'], 1):
                step_num = step_result.get('step', str(i))
                print(f"\nStep {step_num}:")
                
                if 'command' in step_result:
                    print(f"Command: {step_result['command']}")
                    print(f"Status: {'Success' if step_result.get('status', -1) == 0 else 'Failed'}")
                    if 'output' in step_result:
                        print(f"Output: {step_result['output'][:200]}..." if len(step_result.get('output', '')) > 200 else step_result.get('output', ''))
                
                elif 'browser_action' in step_result:
                    print(f"Browser Action: {step_result['browser_action']}")
                    print(f"Result: {step_result.get('message', '')}")
                
                elif 'results' in step_result:
                    print(f"Action: {step_result.get('action', 'Unknown')}")
                    print(f"Description: {step_result.get('description', '')}")
                    print(f"Results: {len(step_result['results'])} action(s) performed")
            
            print("\nPlan execution completed!")
            
        except Exception as e:
            logger.error(f"Error executing plan: {str(e)}")
            print(f"Error executing plan: {str(e)}")
    
    def _process_user_request(self, request: str):
        """
        Process a user request using the AI Agent.
        """
        if not self.agent:
            print("Error: Agent not initialized")
            return
        
        print(f"\nProcessing: {request}")
        print("Thinking...")
        
        try:
            result = self.agent.process_user_request(request)
            
            # Display AI response
            for action_result in result["results"]:
                if action_result["action"] == "response":
                    print("\nAI Response:")
                    print(action_result["text"])
                
                elif action_result["action"] == "terminal":
                    print(f"\nExecuted command: {action_result['command']}")
                    print(f"Status: {'Success' if action_result['status'] == 0 else 'Failed'}")
                    print(f"Output: {action_result['output']}")
                
                elif action_result["action"] == "browser":
                    print(f"\nBrowser action: {action_result['browser_action']}")
                    print(f"Result: {action_result['message']}")
            
            print()
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            print(f"Error processing request: {str(e)}")
    
    def run_interactive(self):
        """
        Run the CLI in interactive mode.
        """
        if not self.initialize_agent():
            return
        
        self.running = True
        
        print("\nAI Agent CLI")
        print("------------")
        print("Type 'help' for available commands")
        print("Type 'exit' to quit")
        
        while self.running:
            try:
                command = input("\n> ")
                if not self.process_command(command):
                    break
            except EOFError:
                print("\nEOF detected. Exiting...")
                break
            except KeyboardInterrupt:
                print("\nInterrupted. Press Ctrl+C again to exit or Enter to continue.")
                try:
                    input()
                except (KeyboardInterrupt, EOFError):
                    print("\nExiting...")
                    break
            except Exception as e:
                logger.error(f"Error in command loop: {str(e)}")
                print(f"Error: {str(e)}")
        
        self.shutdown()
    
    def run_single_command(self, command: str):
        """
        Run a single command and exit.
        """
        if not self.initialize_agent():
            return
        
        self.running = True
        self.process_command(command)
        self.shutdown()

def main():
    """
    Main entry point for the CLI.
    """
    parser = argparse.ArgumentParser(description="AI Agent Command Line Interface")
    parser.add_argument("--api-key", help="OpenAI API key")
    parser.add_argument("--headless", action="store_true", default=True, help="Run browser in headless mode")
    parser.add_argument("--visible-browser", dest="headless", action="store_false", help="Run browser in visible mode")
    parser.add_argument("--command", help="Run a single command and exit")
    parser.add_argument("--execute", help="Execute a terminal command and exit")
    parser.add_argument("--browse", help="Navigate to a URL and exit")
    parser.add_argument("--plan", help="Execute a plan for a goal and exit")
    args = parser.parse_args()
    
    # Create the CLI
    cli = AIAgentCLI(api_key=args.api_key, headless=args.headless)
    
    # Run in the appropriate mode
    if args.command:
        cli.run_single_command(args.command)
    elif args.execute:
        cli.run_single_command(f"execute {args.execute}")
    elif args.browse:
        cli.run_single_command(f"browse {args.browse}")
    elif args.plan:
        cli.run_single_command(f"plan {args.plan}")
    else:
        cli.run_interactive()

if __name__ == "__main__":
    main()
