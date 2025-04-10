#!/usr/bin/env python3
"""
Web Interaction Module for AI Agent

This module provides functionality for browser automation,
web navigation, element interaction, and content extraction.
"""

import os
import time
import logging
from typing import Dict, List, Optional, Tuple, Union, Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementNotInteractableException,
    StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('web_interaction')

class WebController:
    """
    A class to handle web browser operations including navigation,
    element interaction, and content extraction.
    """
    
    def __init__(self, headless: bool = True, download_dir: Optional[str] = None):
        """
        Initialize the WebController with a Selenium WebDriver.
        
        Args:
            headless: Whether to run the browser in headless mode.
            download_dir: Directory to save downloaded files.
        """
        self.headless = headless
        self.download_dir = download_dir or os.path.join(os.getcwd(), 'downloads')
        self.driver = None
        self.initialize_driver()
        logger.info(f"Initialized WebController with headless={headless}")
    
    def initialize_driver(self):
        """
        Initialize the Selenium WebDriver with appropriate options.
        """
        try:
            # Create download directory if it doesn't exist
            os.makedirs(self.download_dir, exist_ok=True)
            
            # Set up Chrome options
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            
            # Set download preferences
            prefs = {
                "download.default_directory": self.download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Initialize the WebDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            
            logger.info("WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing WebDriver: {str(e)}")
            raise
    
    def navigate_to(self, url: str) -> bool:
        """
        Navigate to a specified URL.
        
        Args:
            url: The URL to navigate to.
            
        Returns:
            True if navigation was successful, False otherwise.
        """
        try:
            logger.info(f"Navigating to URL: {url}")
            self.driver.get(url)
            return True
        except Exception as e:
            logger.error(f"Error navigating to {url}: {str(e)}")
            return False
    
    def get_current_url(self) -> str:
        """
        Get the current URL.
        
        Returns:
            The current URL.
        """
        return self.driver.current_url
    
    def get_page_title(self) -> str:
        """
        Get the current page title.
        
        Returns:
            The page title.
        """
        return self.driver.title
    
    def get_page_source(self) -> str:
        """
        Get the current page source.
        
        Returns:
            The page source HTML.
        """
        return self.driver.page_source
    
    def find_element(self, by: str, value: str, timeout: int = 10) -> Optional[Any]:
        """
        Find an element on the page.
        
        Args:
            by: The method to locate the element (e.g., By.ID, By.XPATH).
            value: The value to search for.
            timeout: Maximum time to wait for the element.
            
        Returns:
            The WebElement if found, None otherwise.
        """
        try:
            by_method = getattr(By, by.upper())
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by_method, value))
            )
            return element
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"Element not found: {by}={value}, Error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error finding element {by}={value}: {str(e)}")
            return None
    
    def find_elements(self, by: str, value: str, timeout: int = 10) -> List[Any]:
        """
        Find multiple elements on the page.
        
        Args:
            by: The method to locate the elements (e.g., By.CLASS_NAME, By.CSS_SELECTOR).
            value: The value to search for.
            timeout: Maximum time to wait for the elements.
            
        Returns:
            A list of WebElements if found, empty list otherwise.
        """
        try:
            by_method = getattr(By, by.upper())
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by_method, value))
            )
            elements = self.driver.find_elements(by_method, value)
            return elements
        except (TimeoutException, NoSuchElementException):
            logger.warning(f"No elements found: {by}={value}")
            return []
        except Exception as e:
            logger.error(f"Error finding elements {by}={value}: {str(e)}")
            return []
    
    def click_element(self, element_or_locator: Union[Any, Tuple[str, str]], 
                     timeout: int = 10) -> bool:
        """
        Click on an element.
        
        Args:
            element_or_locator: Either a WebElement or a tuple of (by, value).
            timeout: Maximum time to wait for the element to be clickable.
            
        Returns:
            True if click was successful, False otherwise.
        """
        try:
            element = element_or_locator
            
            # If a locator tuple is provided, find the element
            if isinstance(element_or_locator, tuple):
                by, value = element_or_locator
                by_method = getattr(By, by.upper())
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by_method, value))
                )
            
            # Ensure element is clickable
            if element:
                WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, element.get_attribute("outerHTML")))
                )
                element.click()
                logger.info("Element clicked successfully")
                return True
            
            return False
            
        except (TimeoutException, NoSuchElementException, ElementNotInteractableException) as e:
            logger.warning(f"Element not clickable: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error clicking element: {str(e)}")
            return False
    
    def input_text(self, element_or_locator: Union[Any, Tuple[str, str]], 
                  text: str, clear_first: bool = True) -> bool:
        """
        Input text into an element.
        
        Args:
            element_or_locator: Either a WebElement or a tuple of (by, value).
            text: The text to input.
            clear_first: Whether to clear the element before inputting text.
            
        Returns:
            True if input was successful, False otherwise.
        """
        try:
            element = element_or_locator
            
            # If a locator tuple is provided, find the element
            if isinstance(element_or_locator, tuple):
                by, value = element_or_locator
                by_method = getattr(By, by.upper())
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((by_method, value))
                )
            
            # Input text
            if element:
                if clear_first:
                    element.clear()
                element.send_keys(text)
                logger.info(f"Text input successful: {text}")
                return True
            
            return False
            
        except (TimeoutException, NoSuchElementException, ElementNotInteractableException) as e:
            logger.warning(f"Cannot input text to element: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error inputting text: {str(e)}")
            return False
    
    def submit_form(self, element_or_locator: Union[Any, Tuple[str, str]]) -> bool:
        """
        Submit a form.
        
        Args:
            element_or_locator: Either a WebElement or a tuple of (by, value).
            
        Returns:
            True if submission was successful, False otherwise.
        """
        try:
            element = element_or_locator
            
            # If a locator tuple is provided, find the element
            if isinstance(element_or_locator, tuple):
                by, value = element_or_locator
                by_method = getattr(By, by.upper())
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((by_method, value))
                )
            
            # Submit form
            if element:
                element.submit()
                logger.info("Form submitted successfully")
                return True
            
            return False
            
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"Cannot submit form: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error submitting form: {str(e)}")
            return False
    
    def press_key(self, key: str) -> bool:
        """
        Press a keyboard key.
        
        Args:
            key: The key to press (e.g., Keys.ENTER, Keys.TAB).
            
        Returns:
            True if key press was successful, False otherwise.
        """
        try:
            # Get the key attribute from Keys class
            key_attr = getattr(Keys, key.upper())
            
            # Send the key to the active element
            self.driver.switch_to.active_element.send_keys(key_attr)
            logger.info(f"Key pressed: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error pressing key {key}: {str(e)}")
            return False
    
    def scroll_to_element(self, element_or_locator: Union[Any, Tuple[str, str]]) -> bool:
        """
        Scroll to an element.
        
        Args:
            element_or_locator: Either a WebElement or a tuple of (by, value).
            
        Returns:
            True if scroll was successful, False otherwise.
        """
        try:
            element = element_or_locator
            
            # If a locator tuple is provided, find the element
            if isinstance(element_or_locator, tuple):
                by, value = element_or_locator
                by_method = getattr(By, by.upper())
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((by_method, value))
                )
            
            # Scroll to element
            if element:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                logger.info("Scrolled to element successfully")
                return True
            
            return False
            
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"Cannot scroll to element: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error scrolling to element: {str(e)}")
            return False
    
    def scroll_to_position(self, x: int = 0, y: int = 0) -> bool:
        """
        Scroll to a specific position.
        
        Args:
            x: Horizontal scroll position.
            y: Vertical scroll position.
            
        Returns:
            True if scroll was successful, False otherwise.
        """
        try:
            self.driver.execute_script(f"window.scrollTo({x}, {y});")
            logger.info(f"Scrolled to position: x={x}, y={y}")
            return True
        except Exception as e:
            logger.error(f"Error scrolling to position: {str(e)}")
            return False
    
    def scroll_to_bottom(self) -> bool:
        """
        Scroll to the bottom of the page.
        
        Returns:
            True if scroll was successful, False otherwise.
        """
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            logger.info("Scrolled to bottom of page")
            return True
        except Exception as e:
            logger.error(f"Error scrolling to bottom: {str(e)}")
            return False
    
    def wait_for_element(self, by: str, value: str, 
                        timeout: int = 10, condition: str = "presence") -> Optional[Any]:
        """
        Wait for an element with a specific condition.
        
        Args:
            by: The method to locate the element (e.g., By.ID, By.XPATH).
            value: The value to search for.
            timeout: Maximum time to wait for the element.
            condition: The condition to wait for (presence, visibility, clickable).
            
        Returns:
            The WebElement if found, None otherwise.
        """
        try:
            by_method = getattr(By, by.upper())
            
            if condition == "presence":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by_method, value))
                )
            elif condition == "visibility":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((by_method, value))
                )
            elif condition == "clickable":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by_method, value))
                )
            else:
                logger.warning(f"Unknown condition: {condition}")
                return None
            
            return element
            
        except TimeoutException:
            logger.warning(f"Timeout waiting for element: {by}={value}, condition={condition}")
            return None
        except Exception as e:
            logger.error(f"Error waiting for element {by}={value}: {str(e)}")
            return None
    
    def wait_for_page_load(self, timeout: int = 30) -> bool:
        """
        Wait for the page to load completely.
        
        Args:
            timeout: Maximum time to wait for page load.
            
        Returns:
            True if page loaded, False otherwise.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            logger.info("Page loaded completely")
            return True
        except TimeoutException:
            logger.warning(f"Timeout waiting for page to load")
            return False
        except Exception as e:
            logger.error(f"Error waiting for page load: {str(e)}")
            return False
    
    def extract_text(self, element_or_locator: Optional[Union[Any, Tuple[str, str]]] = None) -> str:
        """
        Extract text from an element or the entire page.
        
        Args:
            element_or_locator: Either a WebElement, a tuple of (by, value), or None for entire page.
            
        Returns:
            The extracted text.
        """
        try:
            # If no element is provided, extract text from the entire page
            if element_or_locator is None:
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                return soup.get_text(separator=' ', strip=True)
            
            element = element_or_locator
            
            # If a locator tuple is provided, find the element
            if isinstance(element_or_locator, tuple):
                by, value = element_or_locator
                by_method = getattr(By, by.upper())
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((by_method, value))
                )
            
            # Extract text from element
            if element:
                return element.text
            
            return ""
            
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            logger.warning(f"Cannot extract text: {str(e)}")
            return ""
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return ""
    
    def extract_links(self, element_or_locator: Optional[Union[Any, Tuple[str, str]]] = None) -> List[Dict[str, str]]:
        """
        Extract links from an element or the entire page.
        
        Args:
            element_or_locator: Either a WebElement, a tuple of (by, value), or None for entire page.
            
        Returns:
            A list of dictionaries with 'text' and 'href' keys.
        """
        try:
            links = []
            
            # If no element is provided, extract links from the entire page
            if element_or_locator is None:
                elements = self.driver.find_elements(By.TAG_NAME, "a")
            else:
                element = element_or_locator
                
                # If a locator tuple is provided, find the element
                if isinstance(element_or_locator, tuple):
                    by, value = element_or_locator
                    by_method = getattr(By, by.upper())
                    element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((by_method, value))
                    )
                
                # Extract links from element
                if element:
                    elements = element.find_elements(By.TAG_NAME, "a")
                else:
                    return []
            
            # Process links
            for link in elements:
                href = link.get_attribute("href")
                text = link.text.strip()
                if href and text:
                    links.append({"text": text, "href": href})
            
            return links
            
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            logger.warning(f"Cannot extract links: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error extracting links: {str(e)}")
            return []
    
    def take_screenshot(self, filename: str) -> bool:
        """
        Take a screenshot of the current page.
        
        Args:
            filename: The filename to save the screenshot.
            
        Returns:
            True if screenshot was saved, False otherwise.
        """
        try:
            # Ensure the filename has a .png extension
            if not filename.lower().endswith('.png'):
                filename += '.png'
            
            # Take screenshot
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return False
    
    def execute_javascript(self, script: str, *args) -> Any:
        """
        Execute JavaScript code.
        
        Args:
            script: The JavaScript code to execute.
            *args: Arguments to pass to the JavaScript code.
            
        Returns:
            The result of the JavaScript execution.
        """
        try:
            result = self.driver.execute_script(script, *args)
            logger.info("JavaScript executed successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing JavaScript: {str(e)}")
            return None
    
    def close(self):
        """
        Close the browser and clean up resources.
        """
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")
    
    def __del__(self):
        """
        Destructor to ensure browser is closed when object is deleted.
        """
        self.close()

# Example usage
if __name__ == "__main__":
    # Create a web controller
    web = WebController(headless=True)
    
    try:
        # Navigate to a website
        web.navigate_to("https://www.example.com")
        
        # Wait for page to load
        web.wait_for_page_load()
        
        # Get page title
        title = web.get_page_title()
        print(f"Page title: {title}")
        
        # Extract text from the page
        text = web.extract_text()
        print(f"Page text: {text}")
        
        # Extract links from the page
        links = web.extract_links()
        print(f"Found {len(links)} links:")
        for link in links:
            print(f"  - {link['text']}: {link['href']}")
        
        # Take a screenshot
        web.take_screenshot("example_screenshot.png")
        
    finally:
        # Close the browser
        web.close()
