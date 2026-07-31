import logging
import sys
from datetime import datetime

def setup_logger():
    """Setup logger configuration"""
    
    # Create logger
    logger = logging.getLogger('bookstore_api')
    logger.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (prints to terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    
    # File handler (saves to file)
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Create logger instance
logger = setup_logger()