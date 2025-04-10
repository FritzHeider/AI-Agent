#!/usr/bin/env python3
"""
AI Agent System - Installation Script

This script helps users install the AI Agent system by setting up
the required dependencies and configuration.
"""

import os
import sys
import subprocess
import argparse
import platform
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    required_version = (3, 10)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current version: {current_version[0]}.{current_version[1]}")
        return False
    
    print(f"Python version check passed: {current_version[0]}.{current_version[1]}.{current_version[2]}")
    return True

def install_dependencies():
    """Install required Python packages."""
    print("Installing required packages...")
    
    packages = [
        "selenium",
        "beautifulsoup4",
        "openai",
        "langchain",
        "webdriver-manager",
        "python-dotenv"
    ]
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install"] + packages, check=True)
        print("All packages installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        return False

def setup_environment():
    """Set up environment configuration."""
    print("Setting up environment configuration...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("Error: .env.example file not found.")
        return False
    
    if not env_file.exists():
        shutil.copy(env_example, env_file)
        print(".env file created from example. Please edit it to add your OpenAI API key.")
    else:
        print(".env file already exists. Make sure it contains your OpenAI API key.")
    
    return True

def check_browser():
    """Check if Chrome browser is installed."""
    print("Checking for Chrome browser...")
    
    system = platform.system()
    
    if system == "Windows":
        chrome_paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                print(f"Chrome found at: {path}")
                return True
    
    elif system == "Darwin":  # macOS
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            print(f"Chrome found at: {chrome_path}")
            return True
    
    elif system == "Linux":
        try:
            result = subprocess.run(["which", "google-chrome"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Chrome found at: {result.stdout.strip()}")
                return True
        except:
            pass
    
    print("Warning: Chrome browser not found. It's required for web interaction.")
    print("Please install Chrome browser before using the web interaction features.")
    return False

def verify_installation():
    """Verify the installation by running a simple test."""
    print("Verifying installation...")
    
    try:
        # Import key modules to verify they're installed correctly
        import_test = subprocess.run(
            [sys.executable, "-c", "import selenium, bs4, openai, langchain, webdriver_manager, dotenv"],
            capture_output=True,
            text=True
        )
        
        if import_test.returncode != 0:
            print(f"Error importing modules: {import_test.stderr}")
            return False
        
        # Try to import our own modules
        import_our_modules = subprocess.run(
            [sys.executable, "-c", "import sys; sys.path.append('.'); import terminal_control, web_interaction, ai_decision"],
            capture_output=True,
            text=True
        )
        
        if import_our_modules.returncode != 0:
            print(f"Error importing AI Agent modules: {import_our_modules.stderr}")
            return False
        
        print("All modules imported successfully.")
        return True
    
    except Exception as e:
        print(f"Error verifying installation: {e}")
        return False

def main():
    """Main installation function."""
    parser = argparse.ArgumentParser(description="AI Agent Installation Script")
    parser.add_argument("--skip-checks", action="store_true", help="Skip environment checks")
    parser.add_argument("--no-verify", action="store_true", help="Skip verification")
    args = parser.parse_args()
    
    print("=== AI Agent Installation ===")
    
    if not args.skip_checks:
        # Check Python version
        if not check_python_version():
            sys.exit(1)
        
        # Check for Chrome browser
        check_browser()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Set up environment
    if not setup_environment():
        sys.exit(1)
    
    # Verify installation
    if not args.no_verify and not verify_installation():
        print("Installation verification failed. The system may not work correctly.")
        sys.exit(1)
    
    print("\nInstallation completed successfully!")
    print("\nNext steps:")
    print("1. Edit the .env file to add your OpenAI API key")
    print("2. Run the agent with: python cli.py")
    print("3. Type 'help' in the CLI for available commands")

if __name__ == "__main__":
    main()
