#!/usr/bin/env python3
"""
Terminal Control Module for AI Agent

This module provides functionality for executing shell commands,
parsing command outputs, and handling errors in terminal operations.
"""

import subprocess
import shlex
import os
import logging
from typing import Dict, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('terminal_control')

class TerminalController:
    """
    A class to handle terminal operations including command execution,
    output parsing, and error handling.
    """
    
    def __init__(self, working_dir: Optional[str] = None):
        """
        Initialize the TerminalController.
        
        Args:
            working_dir: The working directory for command execution.
                         If None, uses the current directory.
        """
        self.working_dir = working_dir or os.getcwd()
        logger.info(f"Initialized TerminalController with working directory: {self.working_dir}")
    
    def execute_command(self, command: str, timeout: int = 60, 
                        capture_output: bool = True) -> Dict[str, Union[int, str, List[str]]]:
        """
        Execute a shell command and return the result.
        
        Args:
            command: The command to execute.
            timeout: Maximum time in seconds to wait for command completion.
            capture_output: Whether to capture and return command output.
            
        Returns:
            A dictionary containing:
                - status: The exit code (0 typically means success)
                - stdout: The standard output as a string
                - stderr: The standard error as a string
                - stdout_lines: The standard output split into lines
                - stderr_lines: The standard error split into lines
                - command: The original command that was executed
        """
        logger.info(f"Executing command: {command}")
        
        try:
            # Use shlex to properly handle command arguments
            if isinstance(command, str):
                args = shlex.split(command)
            else:
                args = command
                
            # Execute the command
            process = subprocess.run(
                args,
                cwd=self.working_dir,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            
            # Prepare the result
            result = {
                'status': process.returncode,
                'command': command,
            }
            
            if capture_output:
                result['stdout'] = process.stdout
                result['stderr'] = process.stderr
                result['stdout_lines'] = process.stdout.splitlines() if process.stdout else []
                result['stderr_lines'] = process.stderr.splitlines() if process.stderr else []
            
            logger.info(f"Command executed with status: {process.returncode}")
            return result
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout} seconds: {command}")
            return {
                'status': -1,
                'command': command,
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds',
                'stdout_lines': [],
                'stderr_lines': [f'Command timed out after {timeout} seconds']
            }
            
        except Exception as e:
            logger.error(f"Error executing command: {command}, Error: {str(e)}")
            return {
                'status': -1,
                'command': command,
                'stdout': '',
                'stderr': str(e),
                'stdout_lines': [],
                'stderr_lines': [str(e)]
            }
    
    def execute_interactive_command(self, command: str, 
                                   inputs: List[str] = None) -> Dict[str, Union[int, str, List[str]]]:
        """
        Execute an interactive command that requires input during execution.
        
        Args:
            command: The command to execute.
            inputs: A list of inputs to provide to the command when prompted.
            
        Returns:
            A dictionary with the command result (same format as execute_command).
        """
        logger.info(f"Executing interactive command: {command}")
        
        if inputs is None:
            inputs = []
            
        try:
            # Use shlex to properly handle command arguments
            if isinstance(command, str):
                args = shlex.split(command)
            else:
                args = command
                
            # Start the process
            process = subprocess.Popen(
                args,
                cwd=self.working_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Prepare to collect output
            stdout_data = []
            stderr_data = []
            
            # Provide inputs if any
            for input_text in inputs:
                stdout, stderr = process.communicate(input=input_text + '\n', timeout=10)
                if stdout:
                    stdout_data.append(stdout)
                if stderr:
                    stderr_data.append(stderr)
            
            # Get any remaining output
            final_stdout, final_stderr = process.communicate(timeout=10)
            if final_stdout:
                stdout_data.append(final_stdout)
            if final_stderr:
                stderr_data.append(final_stderr)
            
            # Prepare the result
            stdout_combined = ''.join(stdout_data)
            stderr_combined = ''.join(stderr_data)
            
            result = {
                'status': process.returncode,
                'command': command,
                'stdout': stdout_combined,
                'stderr': stderr_combined,
                'stdout_lines': stdout_combined.splitlines() if stdout_combined else [],
                'stderr_lines': stderr_combined.splitlines() if stderr_combined else []
            }
            
            logger.info(f"Interactive command executed with status: {process.returncode}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing interactive command: {command}, Error: {str(e)}")
            return {
                'status': -1,
                'command': command,
                'stdout': '',
                'stderr': str(e),
                'stdout_lines': [],
                'stderr_lines': [str(e)]
            }
    
    def parse_command_output(self, output: str, 
                            pattern: Optional[str] = None) -> List[str]:
        """
        Parse command output, optionally filtering by a pattern.
        
        Args:
            output: The command output to parse.
            pattern: Optional regex pattern to filter the output.
            
        Returns:
            A list of output lines, filtered by pattern if provided.
        """
        lines = output.splitlines()
        
        if pattern:
            import re
            pattern_compiled = re.compile(pattern)
            return [line for line in lines if pattern_compiled.search(line)]
        
        return lines
    
    def change_directory(self, directory: str) -> bool:
        """
        Change the working directory for subsequent commands.
        
        Args:
            directory: The directory to change to.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            if os.path.exists(directory) and os.path.isdir(directory):
                self.working_dir = directory
                logger.info(f"Changed working directory to: {directory}")
                return True
            else:
                logger.error(f"Directory does not exist: {directory}")
                return False
        except Exception as e:
            logger.error(f"Error changing directory to {directory}: {str(e)}")
            return False
    
    def get_system_info(self) -> Dict[str, str]:
        """
        Get basic system information.
        
        Returns:
            A dictionary containing system information.
        """
        info = {}
        
        # Get OS information
        os_info = self.execute_command("uname -a")
        if os_info['status'] == 0:
            info['os'] = os_info['stdout'].strip()
        
        # Get CPU information
        cpu_info = self.execute_command("cat /proc/cpuinfo | grep 'model name' | head -1")
        if cpu_info['status'] == 0 and cpu_info['stdout_lines']:
            info['cpu'] = cpu_info['stdout_lines'][0].split(':', 1)[1].strip() if ':' in cpu_info['stdout_lines'][0] else cpu_info['stdout_lines'][0]
        
        # Get memory information
        mem_info = self.execute_command("free -h")
        if mem_info['status'] == 0:
            info['memory'] = mem_info['stdout'].strip()
        
        # Get disk information
        disk_info = self.execute_command("df -h")
        if disk_info['status'] == 0:
            info['disk'] = disk_info['stdout'].strip()
        
        return info

# Example usage
if __name__ == "__main__":
    # Create a terminal controller
    terminal = TerminalController()
    
    # Execute a simple command
    result = terminal.execute_command("ls -la")
    print(f"Command status: {result['status']}")
    print(f"Command output:\n{result['stdout']}")
    
    # Get system information
    system_info = terminal.get_system_info()
    print("\nSystem Information:")
    for key, value in system_info.items():
        print(f"{key}: {value}")
