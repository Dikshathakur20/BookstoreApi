import logging
import sys
import os

def setup_logger():
    logger = logging.getLogger('bookstore_api')
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler - ye Vercel par kaam karega
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # ✅ File handler - ONLY for local development
    if not os.getenv('VERCEL'):
        try:
            file_handler = logging.FileHandler('app.log')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"File logging disabled: {e}")
    
    return logger

logger = setup_logger()