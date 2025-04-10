#!/usr/bin/env python3
"""
AI Agent System - Modified Integration Test

This script tests the integration of the AI Agent components
without initializing the web browser to avoid timeout issues.
"""

import sys
import os
sys.path.append('/home/ubuntu/ai_agent')

# Import only the necessary components for testing
from terminal_control import TerminalController
from ai_decision import AIDecisionMaker

# Mock the WebController to avoid browser initialization
class MockWebController:
    def __init__(self, headless=True):
        self.headless = headless
        print("Mock WebController initialized")
    
    def get_current_url(self):
        return "mock://example.com"
    
    def get_page_title(self):
        return "Mock Page Title"
    
    def close(self):
        print("Mock WebController closed")

# Import and patch the AIAgent class
from ai_agent import AIAgent

# Save the original WebController
original_import = __import__

# Define a custom import function to replace WebController with MockWebController
def custom_import(name, *args, **kwargs):
    module = original_import(name, *args, **kwargs)
    if name == 'web_interaction':
        module.WebController = MockWebController
    return module

# Apply the patch
sys.__import__ = custom_import

# Now test the AIAgent with the mock
try:
    print('Testing AI Agent integration with mock web controller...')
    agent = AIAgent()
    print('AI Agent initialized successfully')
    
    # Test basic functionality
    print('\nTesting component integration:')
    print(f'- Terminal controller initialized: {agent.terminal is not None}')
    print(f'- Web controller initialized: {agent.web is not None}')
    print(f'- AI decision maker initialized: {agent.ai is not None}')
    
    # Test context management
    agent.update_context()
    print(f'- Context management working: {agent.current_context is not None}')
    print(f'- Current directory in context: {agent.current_context["terminal_dir"]}')
    print(f'- Browser URL in context: {agent.current_context["browser_url"]}')
    
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
    print(f'- Action parsing working: {len(actions) > 0}')
    print(f'- Number of actions parsed: {len(actions)}')
    for i, action in enumerate(actions):
        print(f'  Action {i+1}: {action["type"]}')
    
    # Test terminal command execution
    result = agent.execute_terminal_command("echo 'Integration test successful'")
    print(f'- Terminal command execution: {"Success" if result["status"] == 0 else "Failed"}')
    print(f'  Output: {result["stdout"]}')
    
    # Close the agent
    agent.close()
    print('\nAI Agent integration test completed successfully')
except Exception as e:
    print(f'Error during integration test: {str(e)}')
finally:
    # Restore original import
    sys.__import__ = original_import
