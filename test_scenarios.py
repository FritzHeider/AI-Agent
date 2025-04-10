#!/usr/bin/env python3
"""
AI Agent System - Test Scenarios

This module provides test scenarios for verifying the functionality
of the AI Agent system across terminal control, web interaction,
and AI decision-making capabilities.
"""

import os
import sys
import time
import logging
from typing import Dict, List, Any

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the AI Agent components
from terminal_control import TerminalController
from web_interaction import WebController
from ai_decision import AIDecisionMaker
from ai_agent import AIAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_scenarios.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_scenarios')

class TestScenarios:
    """
    Test scenarios for the AI Agent system.
    """
    
    def __init__(self):
        """
        Initialize the test scenarios.
        """
        self.results = {
            "terminal_tests": [],
            "web_tests": [],
            "ai_tests": [],
            "integration_tests": []
        }
        logger.info("Test scenarios initialized")
    
    def run_all_tests(self):
        """
        Run all test scenarios.
        """
        logger.info("Running all test scenarios")
        
        # Run terminal control tests
        self.test_terminal_control()
        
        # Run web interaction tests
        self.test_web_interaction()
        
        # Run AI decision-making tests
        self.test_ai_decision_making()
        
        # Run integration tests
        self.test_integration()
        
        # Print summary
        self.print_summary()
    
    def test_terminal_control(self):
        """
        Test terminal control functionality.
        """
        logger.info("Testing terminal control functionality")
        print("\n=== Terminal Control Tests ===\n")
        
        try:
            # Initialize terminal controller
            terminal = TerminalController()
            
            # Test 1: Execute simple command
            print("Test 1: Execute simple command")
            result = terminal.execute_command("echo 'Hello, Terminal Control!'")
            success = result["status"] == 0 and "Hello, Terminal Control!" in result["stdout"]
            self.results["terminal_tests"].append({
                "name": "Execute simple command",
                "success": success,
                "details": result
            })
            print(f"Result: {'Success' if success else 'Failed'}")
            print(f"Output: {result['stdout']}")
            
            # Test 2: Execute command with error
            print("\nTest 2: Execute command with error")
            result = terminal.execute_command("ls /nonexistent_directory")
            success = result["status"] != 0 and "No such file or directory" in result["stderr"]
            self.results["terminal_tests"].append({
                "name": "Execute command with error",
                "success": success,
                "details": result
            })
            print(f"Result: {'Success' if success else 'Failed'}")
            print(f"Error: {result['stderr']}")
            
            # Test 3: Parse command output
            print("\nTest 3: Parse command output")
            result = terminal.execute_command("echo 'Line 1\nLine 2\nLine 3'")
            parsed = terminal.parse_command_output(result["stdout"])
            success = len(parsed) == 3 and parsed[1] == "Line 2"
            self.results["terminal_tests"].append({
                "name": "Parse command output",
                "success": success,
                "details": {"parsed": parsed}
            })
            print(f"Result: {'Success' if success else 'Failed'}")
            print(f"Parsed lines: {parsed}")
            
            # Test 4: Change directory
            print("\nTest 4: Change directory")
            original_dir = terminal.working_dir
            success = terminal.change_directory("/tmp")
            new_dir = terminal.working_dir
            self.results["terminal_tests"].append({
                "name": "Change directory",
                "success": success and new_dir == "/tmp",
                "details": {"original": original_dir, "new": new_dir}
            })
            print(f"Result: {'Success' if success else 'Failed'}")
            print(f"Changed from {original_dir} to {new_dir}")
            
            # Restore original directory
            terminal.change_directory(original_dir)
            
            print("\nTerminal control tests completed")
            
        except Exception as e:
            logger.error(f"Error in terminal control tests: {str(e)}")
            print(f"Error: {str(e)}")
    
    def test_web_interaction(self):
        """
        Test web interaction functionality.
        """
        logger.info("Testing web interaction functionality")
        print("\n=== Web Interaction Tests ===\n")
        
        try:
            # Initialize web controller with headless browser
            web = WebController(headless=True)
            
            try:
                # Test 1: Navigate to website
                print("Test 1: Navigate to website")
                success = web.navigate_to("https://example.com")
                title = web.get_page_title()
                url = web.get_current_url()
                self.results["web_tests"].append({
                    "name": "Navigate to website",
                    "success": success and "Example" in title,
                    "details": {"title": title, "url": url}
                })
                print(f"Result: {'Success' if success else 'Failed'}")
                print(f"Title: {title}")
                print(f"URL: {url}")
                
                # Test 2: Extract text
                print("\nTest 2: Extract text")
                text = web.extract_text()
                success = len(text) > 0 and "Example Domain" in text
                self.results["web_tests"].append({
                    "name": "Extract text",
                    "success": success,
                    "details": {"text_length": len(text), "sample": text[:100]}
                })
                print(f"Result: {'Success' if success else 'Failed'}")
                print(f"Text sample: {text[:100]}...")
                
                # Test 3: Extract links
                print("\nTest 3: Extract links")
                links = web.extract_links()
                success = len(links) > 0
                self.results["web_tests"].append({
                    "name": "Extract links",
                    "success": success,
                    "details": {"link_count": len(links), "links": links[:3]}
                })
                print(f"Result: {'Success' if success else 'Failed'}")
                print(f"Found {len(links)} links")
                for i, link in enumerate(links[:3]):
                    print(f"  Link {i+1}: {link.get('text', 'No text')} -> {link.get('href', 'No URL')}")
                
                # Test 4: Take screenshot
                print("\nTest 4: Take screenshot")
                screenshot_path = os.path.join(os.getcwd(), "test_screenshot.png")
                success = web.take_screenshot(screenshot_path)
                self.results["web_tests"].append({
                    "name": "Take screenshot",
                    "success": success and os.path.exists(screenshot_path),
                    "details": {"path": screenshot_path}
                })
                print(f"Result: {'Success' if success else 'Failed'}")
                print(f"Screenshot saved to: {screenshot_path}")
                
            finally:
                # Close the browser
                web.close()
            
            print("\nWeb interaction tests completed")
            
        except Exception as e:
            logger.error(f"Error in web interaction tests: {str(e)}")
            print(f"Error: {str(e)}")
    
    def test_ai_decision_making(self):
        """
        Test AI decision-making functionality.
        """
        logger.info("Testing AI decision-making functionality")
        print("\n=== AI Decision-Making Tests ===\n")
        
        try:
            # Initialize AI decision maker
            ai = AIDecisionMaker()
            
            # Test 1: Test conversation history management
            print("Test 1: Conversation history management")
            ai.add_to_history("user", "Hello, AI!")
            ai.add_to_history("assistant", "Hello! How can I help you?")
            success = len(ai.conversation_history) >= 2
            self.results["ai_tests"].append({
                "name": "Conversation history management",
                "success": success,
                "details": {"history_length": len(ai.conversation_history)}
            })
            print(f"Result: {'Success' if success else 'Failed'}")
            print(f"History length: {len(ai.conversation_history)}")
            
            # Test 2: Test system prompt setting
            print("\nTest 2: System prompt setting")
            original_prompt = ai.system_prompt
            new_prompt = "You are a helpful assistant for testing."
            ai.set_system_prompt(new_prompt)
            success = ai.system_prompt == new_prompt
            self.results["ai_tests"].append({
                "name": "System prompt setting",
                "success": success,
                "details": {"original": original_prompt, "new": ai.system_prompt}
            })
            print(f"Result: {'Success' if success else 'Failed'}")
            print(f"New system prompt: {ai.system_prompt}")
            
            # Test 3: Test action parsing from response
            print("\nTest 3: Action parsing from response")
            test_response = """
            You should execute this command:
            ```bash
            ls -la
            ```
            
            And then navigate to this website:
            BROWSER_ACTION: navigate url=https://example.com
            """
            
            # Create a simple parser similar to the one in AIAgent
            import re
            actions = []
            
            # Look for terminal commands in code blocks
            terminal_cmd_pattern = r"```(?:bash|shell|sh)?\s*(.*?)\s*```"
            terminal_matches = re.findall(terminal_cmd_pattern, test_response, re.DOTALL)
            
            for cmd in terminal_matches:
                actions.append({
                    "type": "terminal",
                    "command": cmd.strip()
                })
            
            # Look for browser actions in structured format
            browser_action_pattern = r"BROWSER_ACTION:\s*(\w+)(?:\s+(.+))?"
            browser_matches = re.findall(browser_action_pattern, test_response)
            
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
            
            success = len(actions) == 2
            self.results["ai_tests"].append({
                "name": "Action parsing from response",
                "success": success,
                "details": {"actions": actions}
            })
            print(f"Result: {'Success' if success else 'Failed'}")
            print(f"Parsed {len(actions)} actions:")
            for i, action in enumerate(actions):
                print(f"  Action {i+1}: {action['type']}")
                if action['type'] == 'terminal':
                    print(f"    Command: {action['command']}")
                elif action['type'] == 'browser':
                    print(f"    Browser action: {action['action']}")
                    print(f"    Params: {action['params']}")
            
            # Test 4: Reset conversation history
            print("\nTest 4: Reset conversation history")
            original_length = len(ai.conversation_history)
            ai.reset_history()
            new_length = len(ai.conversation_history)
            success = new_length < original_length
            self.results["ai_tests"].append({
                "name": "Reset conversation history",
                "success": success,
                "details": {"original_length": original_length, "new_length": new_length}
            })
            print(f"Result: {'Success' if success else 'Failed'}")
            print(f"History length before: {original_length}, after: {new_length}")
            
            print("\nAI decision-making tests completed")
            
        except Exception as e:
            logger.error(f"Error in AI decision-making tests: {str(e)}")
            print(f"Error: {str(e)}")
    
    def test_integration(self):
        """
        Test integration of all components.
        """
        logger.info("Testing integration of all components")
        print("\n=== Integration Tests ===\n")
        
        try:
            # Test 1: Test action parsing in AIAgent
            print("Test 1: Action parsing in AIAgent")
            
            # Create a mock WebController to avoid browser initialization
            class MockWebController:
                def __init__(self, headless=True):
                    self.headless = headless
                
                def get_current_url(self):
                    return "mock://example.com"
                
                def get_page_title(self):
                    return "Mock Page Title"
                
                def close(self):
                    pass
            
            # Save the original WebController
            import web_interaction
            original_web_controller = web_interaction.WebController
            
            # Replace with mock
            web_interaction.WebController = MockWebController
            
            # Initialize AIAgent with mock
            agent = AIAgent()
            
            # Test action parsing
            test_response = """
            You should execute this command:
            ```bash
            ls -la
            ```
            
            And then navigate to this website:
            BROWSER_ACTION: navigate url=https://example.com
            """
            
            actions = agent._parse_actions_from_response(test_response)
            success = len(actions) > 0
            self.results["integration_tests"].append({
                "name": "Action parsing in AIAgent",
                "success": success,
                "details": {"actions": actions}
            })
            print(f"Result: {'Success' if success else 'Failed'}")
            print(f"Parsed {len(actions)} actions")
            for i, action in enumerate(actions):
                print(f"  Action {i+1}: {action['type']}")
            
            # Test 2: Test terminal command execution in AIAgent
            print("\nTest 2: Terminal command execution in AIAgent")
            result = agent.execute_terminal_command("echo 'Integration test'")
            success = result["status"] == 0 and "Integration test" in result["stdout"]
            self.results["integration_tests"].append({
                "name": "Terminal command execution in AIAgent",
                "success": success,
                "details": result
            })
            print(f"Result: {'Success' if success else 'Failed'}")
            print(f"Command output: {result['stdout']}")
            
            # Test 3: Test context management in AIAgent
            print("\nTest 3: Context management in AIAgent")
            agent.update_context()
            context = agent.current_context
            success = "terminal_dir" in context and "browser_url" in context
            self.results["integration_tests"].append({
                "name": "Context management in AIAgent",
                "success": success,
                "details": {"context_keys": list(context.keys())}
            })
            print(f"Result: {'Success' if success else 'Failed'}")
            print(f"Context keys: {list(context.keys())}")
            
            # Close the agent
            agent.close()
            
            # Restore original WebController
            web_interaction.WebController = original_web_controller
            
            print("\nIntegration tests completed")
            
        except Exception as e:
            logger.error(f"Error in integration tests: {str(e)}")
            print(f"Error: {str(e)}")
    
    def print_summary(self):
        """
        Print a summary of all test results.
        """
        print("\n=== Test Summary ===\n")
        
        # Count successes and failures
        total_tests = 0
        total_success = 0
        
        for category, tests in self.results.items():
            category_success = sum(1 for test in tests if test["success"])
            category_total = len(tests)
            total_tests += category_total
            total_success += category_success
            
            print(f"{category.replace('_', ' ').title()}: {category_success}/{category_total} passed")
        
        # Print overall success rate
        success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
        print(f"\nOverall: {total_success}/{total_tests} passed ({success_rate:.1f}%)")
        
        # Determine overall status
        if total_success == total_tests:
            print("\nAll tests passed successfully!")
        else:
            print("\nSome tests failed. Check the logs for details.")

# Main function
def main():
    """
    Main entry point for running test scenarios.
    """
    print("AI Agent System - Test Scenarios")
    print("--------------------------------")
    
    # Create and run test scenarios
    tests = TestScenarios()
    tests.run_all_tests()

if __name__ == "__main__":
    main()
