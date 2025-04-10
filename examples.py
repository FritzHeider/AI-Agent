#!/usr/bin/env python3
"""
AI Agent System - Usage Examples

This script demonstrates various usage examples for the AI Agent system.
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the AI Agent components
from ai_agent import AIAgent
from terminal_control import TerminalController
from web_interaction import WebController

# Load environment variables
load_dotenv()

def example_terminal_commands():
    """Example of using terminal commands."""
    print("\n=== Terminal Command Examples ===\n")
    
    # Create a terminal controller
    terminal = TerminalController()
    
    # Example 1: List files in the current directory
    print("Example 1: List files in the current directory")
    result = terminal.execute_command("ls -la")
    print(f"Command status: {result['status']}")
    print(f"Output:\n{result['stdout']}")
    
    # Example 2: Get system information
    print("\nExample 2: Get system information")
    system_info = terminal.get_system_info()
    print("System Information:")
    for key, value in system_info.items():
        print(f"{key}: {value}")
    
    # Example 3: Execute a command with error handling
    print("\nExample 3: Execute a command with error handling")
    result = terminal.execute_command("ls /nonexistent_directory")
    if result['status'] != 0:
        print(f"Command failed with error: {result['stderr']}")
        print("Handling the error gracefully...")
    
    print("\nTerminal command examples completed")

def example_web_interaction():
    """Example of web interaction."""
    print("\n=== Web Interaction Examples ===\n")
    
    # Create a web controller with headless browser
    web = WebController(headless=True)
    
    try:
        # Example 1: Navigate to a website
        print("Example 1: Navigate to a website")
        web.navigate_to("https://example.com")
        web.wait_for_page_load()
        print(f"Page title: {web.get_page_title()}")
        print(f"Current URL: {web.get_current_url()}")
        
        # Example 2: Extract content from a page
        print("\nExample 2: Extract content from a page")
        text = web.extract_text()
        print(f"Page text (first 100 chars): {text[:100]}...")
        
        links = web.extract_links()
        print(f"Found {len(links)} links")
        for i, link in enumerate(links[:3]):
            print(f"  Link {i+1}: {link.get('text', 'No text')} -> {link.get('href', 'No URL')}")
        
        # Example 3: Take a screenshot
        print("\nExample 3: Take a screenshot")
        screenshot_path = os.path.join(os.getcwd(), "example_screenshot.png")
        web.take_screenshot(screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
        
    finally:
        # Close the browser
        web.close()
    
    print("\nWeb interaction examples completed")

def example_integrated_agent():
    """Example of using the integrated AI Agent."""
    print("\n=== Integrated AI Agent Examples ===\n")
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: No OpenAI API key found. AI functionality will be limited.")
        print("Set your API key in the .env file for full functionality.")
    
    # Create an AI Agent
    agent = AIAgent(api_key=api_key)
    
    try:
        # Example 1: Execute a terminal command
        print("Example 1: Execute a terminal command through the agent")
        result = agent.execute_terminal_command("echo 'Hello from the AI Agent!'")
        print(f"Command status: {'Success' if result['status'] == 0 else 'Failed'}")
        print(f"Output: {result['stdout']}")
        
        # Example 2: Execute a browser action
        print("\nExample 2: Execute a browser action through the agent")
        result = agent.execute_browser_action("navigate", url="https://example.com")
        print(f"Browser action result: {result['message']}")
        
        # Example 3: Process a user request (limited without API key)
        print("\nExample 3: Process a user request")
        print("Note: This example requires an OpenAI API key for full functionality")
        
        if api_key:
            result = agent.process_user_request("What is the current directory?")
            print("AI Response:")
            for action_result in result["results"]:
                if action_result["action"] == "response":
                    print(action_result["text"])
        else:
            print("Skipping this example due to missing API key")
        
    finally:
        # Close the agent
        agent.close()
    
    print("\nIntegrated AI Agent examples completed")

def main():
    """Main function to run all examples."""
    print("AI Agent System - Usage Examples")
    print("--------------------------------")
    
    # Run terminal command examples
    example_terminal_commands()
    
    # Run web interaction examples
    example_web_interaction()
    
    # Run integrated agent examples
    example_integrated_agent()
    
    print("\nAll examples completed successfully!")
    print("\nNext steps:")
    print("1. Try running the CLI with: python cli.py")
    print("2. Explore the documentation in README.md")
    print("3. Customize the agent for your specific needs")

if __name__ == "__main__":
    main()
