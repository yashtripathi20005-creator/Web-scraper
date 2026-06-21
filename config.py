"""
Configuration settings for the web scraper
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Scraping settings
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 10))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', 2))
    USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # Output settings
    OUTPUT_FORMAT = os.getenv('OUTPUT_FORMAT', 'json')  # json, csv, or both
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output')
    
    # News sources configuration
    SOURCES = {
        'bbc': {
            'url': 'https://www.bbc.com/news',
            'headline_selector': 'h3',
            'link_selector': 'a',
            'class_filter': 'gs-c-promo-heading__title'
        },
        'cnn': {
            'url': 'https://edition.cnn.com',
            'headline_selector': 'span',
            'link_selector': 'a',
            'class_filter': 'container__headline-text'
        },
        'reuters': {
            'url': 'https://www.reuters.com',
            'headline_selector': 'h3',
            'link_selector': 'a',
            'class_filter': 'story-title'
        },
        'aljazeera': {
            'url': 'https://www.aljazeera.com',
            'headline_selector': 'h3',
            'link_selector': 'a',
            'class_filter': 'gc__title'
        }
    }
