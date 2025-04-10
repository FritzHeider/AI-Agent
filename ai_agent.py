#!/usr/bin/env python3
"""
AI Agent System - Main Integration Module

This module integrates the terminal control, web interaction,
and AI decision-making components into a cohesive agent system.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, List, Optional, Tuple, Union, Any

# Import component modules
from terminal_control import TerminalController
from web_interaction import WebController
from ai_decision import AIDecisionMaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ai_agent')

class AIAgent:
    """
    Main AI Agent class that integrates all components and
    provides a unified interface for agent operations.
    """
    
    def __init__(self, api_key: Optional[str] = None, headless: bool = True):
        """
        Initialize the AI Agent with all its components.
        
        Args:
            api_key: OpenAI API key. If None, tries to get from environment variable.
            headless: Whether to run the browser in headless mode.
        """
        logger.info("Initializing AI Agent system")
        
        # Initialize components
        self.terminal = TerminalController()
        self.web = WebController(headless=headless)
        self.ai = AIDecisionMaker(api_key=api_key)
        
        # Initialize agent state
        self.current_task = None
        self.task_history = []
        self.current_context = {
            "terminal_dir": self.terminal.working_dir,
            "browser_url": None,
            "last_command": None,
            "last_result": None
        }
        
        logger.info("AI Agent system initialized successfully")
    
    def update_context(self):
        """
        Update the current context with the latest state information.
        """
        self.current_context["terminal_dir"] = self.terminal.working_dir
        
        if hasattr(self.web, 'driver') and self.web.driver:
            try:
                self.current_context["browser_url"] = self.web.get_current_url()
                self.current_context["browser_title"] = self.web.get_page_title()
            except:
                self.current_context["browser_url"] = None
                self.current_context["browser_title"] = None
        
        logger.debug("Context updated")
    
    def execute_terminal_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a terminal command and update context.
        
        Args:
            command: The command to execute.
            
        Returns:
            The command result.
        """
        logger.info(f"Executing terminal command: {command}")
        
        # Execute the command
        result = self.terminal.execute_command(command)
        
        # Update context
        self.current_context["last_command"] = command
        self.current_context["last_result"] = {
            "status": result["status"],
            "stdout": result["stdout"][:500] + ("..." if len(result["stdout"]) > 500 else ""),
            "stderr": result["stderr"][:500] + ("..." if len(result["stderr"]) > 500 else "")
        }
        self.update_context()
        
        return result
    
    def execute_browser_action(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a browser action and update context.
        
        Args:
            action: The browser action to perform (navigate, click, etc.).
            **kwargs: Additional arguments for the action.
            
        Returns:
            The action result.
        """
        logger.info(f"Executing browser action: {action}")
        
        result = {"success": False, "message": "Unknown action"}
        
        # Execute the requested browser action
        if action == "navigate":
            url = kwargs.get("url")
            if url:
                success = self.web.navigate_to(url)
                result = {"success": success, "message": f"Navigated to {url}" if success else f"Failed to navigate to {url}"}
        
        elif action == "click":
            selector_type = kwargs.get("selector_type", "id")
            selector_value = kwargs.get("selector_value")
            if selector_value:
                element = self.web.find_element(selector_type, selector_value)
                if element:
                    success = self.web.click_element(element)
                    result = {"success": success, "message": f"Clicked element {selector_value}" if success else f"Failed to click element {selector_value}"}
                else:
                    result = {"success": False, "message": f"Element not found: {selector_value}"}
        
        elif action == "input":
            selector_type = kwargs.get("selector_type", "id")
            selector_value = kwargs.get("selector_value")
            text = kwargs.get("text", "")
            if selector_value:
                element = self.web.find_element(selector_type, selector_value)
                if element:
                    success = self.web.input_text(element, text)
                    result = {"success": success, "message": f"Input text to element {selector_value}" if success else f"Failed to input text to element {selector_value}"}
                else:
                    result = {"success": False, "message": f"Element not found: {selector_value}"}
        
        elif action == "extract":
            content_type = kwargs.get("content_type", "text")
            if content_type == "text":
                text = self.web.extract_text()
                result = {"success": True, "message": "Text extracted", "content": text[:1000] + ("..." if len(text) > 1000 else "")}
            elif content_type == "links":
                links = self.web.extract_links()
                result = {"success": True, "message": f"Extracted {len(links)} links", "content": links[:20]}
        
        elif action == "screenshot":
            filename = kwargs.get("filename", "screenshot.png")
            success = self.web.take_screenshot(filename)
            result = {"success": success, "message": f"Screenshot saved to {filename}" if success else f"Failed to take screenshot"}
        
        # Update context
        self.current_context["last_browser_action"] = {
            "action": action,
            "params": kwargs,
            "result": result["message"]
        }
        self.update_context()
        
        return result
    
    def process_user_request(self, request: str) -> Dict[str, Any]:
        """
        Process a user request using AI to determine and execute actions.
        
        Args:
            request: The user's request or instruction.
            
        Returns:
            A dictionary with the processing result.
        """
        logger.info(f"Processing user request: {request}")
        
        # Update context before processing
        self.update_context()
        
        # Use AI to determine what to do
        ai_response = self.ai.generate_response(request, self.current_context)
        
        # Parse AI response to extract actions
        actions = self._parse_actions_from_response(ai_response)
        
        # Execute actions
        results = []
        for action in actions:
            action_type = action.get("type")
            
            if action_type == "terminal":
                command = action.get("command")
                if command:
                    result = self.execute_terminal_command(command)
                    results.append({
                        "action": "terminal",
                        "command": command,
                        "status": result["status"],
                        "output": result["stdout"] if result["status"] == 0 else result["stderr"]
                    })
            
            elif action_type == "browser":
                browser_action = action.get("action")
                params = action.get("params", {})
                if browser_action:
                    result = self.execute_browser_action(browser_action, **params)
                    results.append({
                        "action": "browser",
                        "browser_action": browser_action,
                        "params": params,
                        "success": result["success"],
                        "message": result["message"]
                    })
            
            elif action_type == "response":
                # Just a text response, no action needed
                results.append({
                    "action": "response",
                    "text": action.get("text", "")
                })
        
        # If no actions were extracted, treat the entire response as text
        if not actions:
            results.append({
                "action": "response",
                "text": ai_response
            })
        
        # Update task history
        self.task_history.append({
            "request": request,
            "response": ai_response,
            "actions": actions,
            "results": results
        })
        
        return {
            "request": request,
            "ai_response": ai_response,
            "actions": actions,
            "results": results
        }
    
    def _parse_actions_from_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse actions from an AI response.
        
        Args:
            response: The AI-generated response.
            
        Returns:
            A list of action dictionaries.
        """
        actions = []
        
        # Look for terminal commands in code blocks
        import re
        terminal_cmd_pattern = r"```(?:bash|shell|sh)?\s*(.*?)\s*```"
        terminal_matches = re.findall(terminal_cmd_pattern, response, re.DOTALL)
        
        for cmd in terminal_matches:
            # Skip if it looks like code rather than a command
            if len(cmd.splitlines()) > 5 or "def " in cmd or "class " in cmd:
                continue
                
            actions.append({
                "type": "terminal",
                "command": cmd.strip()
            })
        
        # Look for browser actions in structured format
        browser_action_pattern = r"BROWSER_ACTION:\s*(\w+)(?:\s+(.+))?"
        browser_matches = re.findall(browser_action_pattern, response)
        
        for action, params_str in browser_matches:
            params = {}
            if params_str:
                # Parse simple key=value pairs
                for pair in params_str.split():
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        params[key] = value
            
            actions.append({
                "type": "browser",
                "action": action.lower(),
                "params": params
            })
        
        # If no structured actions found, check for common browser action phrases
        if not actions:
            if "navigate to" in response.lower() or "go to" in response.lower():
                url_pattern = r"(?:navigate to|go to)\s+(https?://[^\s]+)"
                url_match = re.search(url_pattern, response.lower())
                if url_match:
                    actions.append({
                        "type": "browser",
                        "action": "navigate",
                        "params": {"url": url_match.group(1)}
                    })
        
        # If we extracted actions, also add the text response
        if actions:
            # Remove the code blocks and action commands from the response
            clean_response = re.sub(terminal_cmd_pattern, "", response)
            clean_response = re.sub(browser_action_pattern, "", clean_response)
            clean_response = clean_response.strip()
            
            actions.append({
                "type": "response",
                "text": clean_response
            })
        
        return actions
    
    def execute_plan(self, goal: str) -> Dict[str, Any]:
        """
        Generate and execute a plan to achieve a goal.
        
        Args:
            goal: The goal to achieve.
            
        Returns:
            A dictionary with the execution result.
        """
        logger.info(f"Executing plan for goal: {goal}")
        
        # Generate a plan
        plan = self.ai.generate_plan(goal)
        
        # Execute each step in the plan
        results = []
        for step in plan:
            step_num = step.get("step", "")
            action = step.get("action", "")
            description = step.get("description", "")
            
            logger.info(f"Executing plan step {step_num}: {action}")
            
            # Process the step based on action type
            if action.lower() in ["terminal", "command", "shell"]:
                # Extract command from description if not explicitly provided
                command = description
                if ":" in description:
                    command = description.split(":", 1)[1].strip()
                
                result = self.execute_terminal_command(command)
                results.append({
                    "step": step_num,
                    "action": action,
                    "command": command,
                    "status": result["status"],
                    "output": result["stdout"] if result["status"] == 0 else result["stderr"]
                })
            
            elif action.lower() in ["browser", "web", "navigate"]:
                # Process as a browser action
                browser_action = "navigate"
                params = {}
                
                # Try to extract URL if it's a navigation action
                if "http" in description:
                    import re
                    url_match = re.search(r"(https?://[^\s]+)", description)
                    if url_match:
                        params["url"] = url_match.group(1)
                
                result = self.execute_browser_action(browser_action, **params)
                results.append({
                    "step": step_num,
                    "action": action,
                    "browser_action": browser_action,
                    "params": params,
                    "success": result["success"],
                    "message": result["message"]
                })
            
            else:
                # Process as a user request
                process_result = self.process_user_request(description)
                results.append({
                    "step": step_num,
                    "action": action,
                    "description": description,
                    "results": process_result["results"]
                })
        
        return {
            "goal": goal,
            "plan": plan,
            "results": results
        }
    
    def close(self):
        """
        Close the agent and clean up resources.
        """
        logger.info("Closing AI Agent system")
        
        # Close components
        if hasattr(self.web, 'close'):
            self.web.close()
        
        logger.info("AI Agent system closed successfully")
    
    def __del__(self):
        """
        Destructor to ensure resources are cleaned up.
        """
        self.close()

# Command-line interface
def main():
    parser = argparse.ArgumentParser(description="AI Agent System")
    parser.add_argument("--api-key", help="OpenAI API key")
    parser.add_argument("--headless", action="store_true", default=True, help="Run browser in headless mode")
    parser.add_argument("--request", help="Process a single request and exit")
    parser.add_argument("--goal", help="Execute a plan to achieve a goal and exit")
    args = parser.parse_args()
    
    # Create the agent
    agent = AIAgent(api_key=args.api_key, headless=args.headless)
    
    try:
        if args.request:
            # Process a single request
            result = agent.process_user_request(args.request)
            print(json.dumps(result, indent=2))
        
        elif args.goal:
            # Execute a plan for a goal
            result = agent.execute_plan(args.goal)
            print(json.dumps(result, indent=2))
        
        else:
            # Interactive mode
            print("AI Agent System")
            print("Type 'exit' to quit")
            
            while True:
                try:
                    request = input("\nEnter request: ")
                    if request.lower() in ["exit", "quit"]:
                        break
                    
                    result = agent.process_user_request(request)
                    
                    # Display results
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
                    
                except KeyboardInterrupt:
                    print("\nInterrupted by user")
                    break
                except Exception as e:
                    print(f"Error: {str(e)}")
    
    finally:
        # Clean up
        agent.close()

if __name__ == "__main__":
    main()
