#!/usr/bin/env python3
"""
AI Decision Making Component for AI Agent

This module provides the AI capabilities for the agent,
enabling it to make decisions, generate commands, and
understand context for intelligent automation.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
import openai
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ai_decision')

# Load environment variables from .env file if it exists
load_dotenv()

class AIDecisionMaker:
    """
    A class to handle AI decision making, command generation,
    and context management for the agent.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize the AIDecisionMaker.
        
        Args:
            api_key: OpenAI API key. If None, tries to get from environment variable.
            model: The AI model to use for decision making.
        """
        # Set API key from parameter or environment variable
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("No OpenAI API key provided. AI functionality will be limited.")
        else:
            openai.api_key = self.api_key
        
        self.model = model
        self.conversation_history = []
        self.system_prompt = """
        You are an AI assistant that helps control a computer by generating commands and making decisions.
        You can:
        1. Execute terminal commands
        2. Navigate and interact with websites
        3. Process information and make decisions based on context
        
        When asked to perform a task:
        - Break it down into steps
        - Generate appropriate commands or actions for each step
        - Provide clear explanations for your decisions
        - Handle errors gracefully
        
        Always prioritize safety and confirm before potentially destructive operations.
        """
        
        logger.info(f"Initialized AIDecisionMaker with model: {model}")
    
    def add_to_history(self, role: str, content: str):
        """
        Add a message to the conversation history.
        
        Args:
            role: The role of the message sender (system, user, assistant).
            content: The message content.
        """
        self.conversation_history.append({"role": role, "content": content})
        
        # Keep history at a reasonable size to avoid token limits
        if len(self.conversation_history) > 20:
            # Remove oldest messages but keep system prompt
            system_messages = [msg for msg in self.conversation_history if msg["role"] == "system"]
            other_messages = [msg for msg in self.conversation_history if msg["role"] != "system"]
            other_messages = other_messages[-19:]  # Keep last 19 non-system messages
            self.conversation_history = system_messages + other_messages
    
    def reset_history(self):
        """
        Reset the conversation history, keeping only the system prompt.
        """
        system_messages = [msg for msg in self.conversation_history if msg["role"] == "system"]
        self.conversation_history = system_messages
        logger.info("Conversation history reset")
    
    def set_system_prompt(self, prompt: str):
        """
        Set or update the system prompt.
        
        Args:
            prompt: The new system prompt.
        """
        # Remove old system prompts
        self.conversation_history = [msg for msg in self.conversation_history if msg["role"] != "system"]
        # Add new system prompt
        self.add_to_history("system", prompt)
        self.system_prompt = prompt
        logger.info("System prompt updated")
    
    def generate_response(self, user_input: str, 
                         context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate an AI response based on user input and context.
        
        Args:
            user_input: The user's input or request.
            context: Additional context information (e.g., current directory, browser state).
            
        Returns:
            The AI-generated response.
        """
        if not self.api_key:
            logger.error("Cannot generate response: No OpenAI API key provided")
            return "Error: AI functionality is not available without an API key."
        
        try:
            # Add context to user input if provided
            if context:
                context_str = "\n\nCurrent context:\n" + json.dumps(context, indent=2)
                enhanced_input = user_input + context_str
            else:
                enhanced_input = user_input
            
            # Add user input to history
            self.add_to_history("user", enhanced_input)
            
            # Ensure system prompt is in history
            if not any(msg["role"] == "system" for msg in self.conversation_history):
                self.conversation_history.insert(0, {"role": "system", "content": self.system_prompt})
            
            # Generate response from OpenAI
            response = openai.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract and process response
            response_text = response.choices[0].message.content
            
            # Add response to history
            self.add_to_history("assistant", response_text)
            
            logger.info("Generated AI response successfully")
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return f"Error generating response: {str(e)}"
    
    def generate_command(self, task_description: str, 
                        command_type: str = "terminal") -> str:
        """
        Generate a specific command based on task description.
        
        Args:
            task_description: Description of the task to accomplish.
            command_type: Type of command to generate (terminal, browser, etc.).
            
        Returns:
            The generated command.
        """
        if not self.api_key:
            logger.error("Cannot generate command: No OpenAI API key provided")
            return "Error: AI functionality is not available without an API key."
        
        try:
            # Create a specialized prompt for command generation
            if command_type == "terminal":
                prompt = f"Generate a Linux terminal command to accomplish this task: {task_description}\nProvide only the command with no explanation."
            elif command_type == "browser":
                prompt = f"Generate a step-by-step instruction for browser interaction to accomplish this task: {task_description}\nFormat as numbered steps."
            else:
                prompt = f"Generate a {command_type} command to accomplish this task: {task_description}\nProvide only the command with no explanation."
            
            # Generate response without adding to conversation history
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates precise commands."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Extract and process command
            command = response.choices[0].message.content.strip()
            
            logger.info(f"Generated {command_type} command successfully")
            return command
            
        except Exception as e:
            logger.error(f"Error generating command: {str(e)}")
            return f"Error generating command: {str(e)}"
    
    def analyze_output(self, command: str, output: str) -> Dict[str, Any]:
        """
        Analyze command output to extract useful information.
        
        Args:
            command: The command that was executed.
            output: The output of the command.
            
        Returns:
            A dictionary with analysis results.
        """
        if not self.api_key:
            logger.error("Cannot analyze output: No OpenAI API key provided")
            return {"error": "AI functionality is not available without an API key."}
        
        try:
            # Create a specialized prompt for output analysis
            prompt = f"Analyze the following command output and extract key information:\n\nCommand: {command}\n\nOutput:\n{output}\n\nProvide analysis as JSON with keys: success (boolean), key_findings (list), next_steps (list)."
            
            # Generate response without adding to conversation history
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes command outputs."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Extract and process analysis
            analysis_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                # Extract JSON if it's wrapped in markdown code blocks
                if "```json" in analysis_text:
                    json_str = analysis_text.split("```json")[1].split("```")[0].strip()
                    analysis = json.loads(json_str)
                else:
                    analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                # If not valid JSON, return as text
                analysis = {
                    "success": None,
                    "key_findings": [analysis_text],
                    "next_steps": []
                }
            
            logger.info("Analyzed command output successfully")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing output: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "key_findings": [],
                "next_steps": []
            }
    
    def extract_entities(self, text: str, entity_types: List[str]) -> Dict[str, List[str]]:
        """
        Extract specific types of entities from text.
        
        Args:
            text: The text to analyze.
            entity_types: Types of entities to extract (e.g., urls, emails, dates).
            
        Returns:
            A dictionary with entity types as keys and lists of extracted entities as values.
        """
        if not self.api_key:
            logger.error("Cannot extract entities: No OpenAI API key provided")
            return {entity_type: [] for entity_type in entity_types}
        
        try:
            # Create a specialized prompt for entity extraction
            entity_types_str = ", ".join(entity_types)
            prompt = f"Extract the following entity types from the text: {entity_types_str}\n\nText:\n{text}\n\nProvide results as JSON with entity types as keys and lists of extracted entities as values."
            
            # Generate response without adding to conversation history
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts entities from text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Extract and process entities
            entities_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                # Extract JSON if it's wrapped in markdown code blocks
                if "```json" in entities_text:
                    json_str = entities_text.split("```json")[1].split("```")[0].strip()
                    entities = json.loads(json_str)
                else:
                    entities = json.loads(entities_text)
            except json.JSONDecodeError:
                # If not valid JSON, return empty lists
                entities = {entity_type: [] for entity_type in entity_types}
            
            logger.info(f"Extracted entities successfully: {entity_types_str}")
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return {entity_type: [] for entity_type in entity_types}
    
    def generate_plan(self, goal: str) -> List[Dict[str, str]]:
        """
        Generate a step-by-step plan to achieve a goal.
        
        Args:
            goal: The goal to achieve.
            
        Returns:
            A list of steps, each as a dictionary with 'step', 'action', and 'description' keys.
        """
        if not self.api_key:
            logger.error("Cannot generate plan: No OpenAI API key provided")
            return [{"step": "1", "action": "Error", "description": "AI functionality is not available without an API key."}]
        
        try:
            # Create a specialized prompt for plan generation
            prompt = f"Generate a detailed step-by-step plan to achieve this goal: {goal}\n\nProvide the plan as JSON with a list of steps, each with 'step' (number), 'action' (command or action type), and 'description' (explanation) keys."
            
            # Generate response without adding to conversation history
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates detailed plans."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            # Extract and process plan
            plan_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                # Extract JSON if it's wrapped in markdown code blocks
                if "```json" in plan_text:
                    json_str = plan_text.split("```json")[1].split("```")[0].strip()
                    plan_data = json.loads(json_str)
                else:
                    plan_data = json.loads(plan_text)
                
                # Ensure the plan is in the expected format
                if isinstance(plan_data, dict) and "steps" in plan_data:
                    plan = plan_data["steps"]
                elif isinstance(plan_data, list):
                    plan = plan_data
                else:
                    plan = [{"step": "1", "action": "Error", "description": "Invalid plan format returned."}]
            except json.JSONDecodeError:
                # If not valid JSON, create a simple plan with the text
                plan = [{"step": "1", "action": "Manual", "description": plan_text}]
            
            logger.info(f"Generated plan successfully for goal: {goal}")
            return plan
            
        except Exception as e:
            logger.error(f"Error generating plan: {str(e)}")
            return [{"step": "1", "action": "Error", "description": f"Error generating plan: {str(e)}"}]

# Example usage
if __name__ == "__main__":
    # Create an AI decision maker (requires API key)
    ai = AIDecisionMaker()
    
    # Example: Generate a response
    if ai.api_key:
        response = ai.generate_response("How can I check the disk space usage on my system?")
        print(f"AI Response: {response}")
        
        # Example: Generate a terminal command
        command = ai.generate_command("Check disk space usage", "terminal")
        print(f"Generated Command: {command}")
        
        # Example: Generate a plan
        plan = ai.generate_plan("Set up a web server and deploy a simple HTML page")
        print("Generated Plan:")
        for step in plan:
            print(f"{step['step']}. {step['action']}: {step['description']}")
    else:
        print("API key not available. Please set the OPENAI_API_KEY environment variable.")
