"""
Core web scraper implementation
"""
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebScraper:
    """Main web scraper class for extracting headlines"""
    
    def __init__(self):
        self.session = self._create_session()
        self.ua = UserAgent()
        self.config = Config()
        
    def _create_session(self) -> requests.Session:
        """Create a session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=self.config.MAX_RETRIES,
            backoff_factor=self.config.RETRY_DELAY,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    def _get_headers(self) -> Dict[str, str]:
        """Generate headers with random user agent"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch a webpage and return BeautifulSoup object
        
        Args:
            url: The URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=self.config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            return BeautifulSoup(response.text, 'lxml')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_headlines(
        self,
        soup: BeautifulSoup,
        selector: str,
        class_filter: str,
        base_url: str
    ) -> List[Dict[str, str]]:
        """
        Extract headlines from BeautifulSoup object
        
        Args:
            soup: BeautifulSoup object
            selector: HTML tag selector (h1, h2, h3, etc.)
            class_filter: CSS class to filter
            base_url: Base URL for constructing full links
            
        Returns:
            List of dictionaries with headline text and links
        """
        headlines = []
        
        try:
            # Find all elements with the given selector
            if class_filter:
                elements = soup.find_all(selector, class_=class_filter)
            else:
                elements = soup.find_all(selector)
            
            # Also search for parent containers that might contain both headline and link
            containers = soup.find_all(['article', 'div', 'li'], class_=lambda x: x and 'story' in x.lower())
            if not containers:
                containers = soup.find_all(['div', 'section'])
            
            # First try: direct elements
            for element in elements:
                headline_text = element.get_text(strip=True)
                if headline_text and len(headline_text) > 10:  # Filter out short text
                    # Find the closest anchor tag
                    link = element.find_parent('a') or element.find('a')
                    if link and link.get('href'):
                        href = link.get('href')
                        full_url = urljoin(base_url, href)
                        headlines.append({
                            'headline': headline_text,
                            'link': full_url
                        })
            
            # Second try: search in containers
            if len(headlines) < 5:
                for container in containers[:20]:  # Limit to first 20 containers
                    headline_elem = container.find(['h1', 'h2', 'h3', 'h4'])
                    if headline_elem:
                        headline_text = headline_elem.get_text(strip=True)
                        if headline_text and len(headline_text) > 10:
                            link = container.find('a')
                            if link and link.get('href'):
                                href = link.get('href')
                                full_url = urljoin(base_url, href)
                                headlines.append({
                                    'headline': headline_text,
                                    'link': full_url
                                })
            
            # Remove duplicates while preserving order
            seen = set()
            unique_headlines = []
            for item in headlines:
                if item['headline'] not in seen:
                    seen.add(item['headline'])
                    unique_headlines.append(item)
            
            logger.info(f"Extracted {len(unique_headlines)} headlines")
            return unique_headlines[:20]  # Return top 20 headlines
            
        except Exception as e:
            logger.error(f"Error extracting headlines: {e}")
            return []
    
    def scrape_source(self, source_name: str, source_config: Dict) -> List[Dict]:
        """
        Scrape headlines from a single source
        
        Args:
            source_name: Name of the source
            source_config: Configuration for the source
            
        Returns:
            List of dictionaries with headline data
        """
        logger.info(f"Scraping {source_name}...")
        
        soup = self.fetch_page(source_config['url'])
        if not soup:
            return []
        
        headlines = self.extract_headlines(
            soup,
            source_config['headline_selector'],
            source_config.get('class_filter', ''),
            source_config['url']
        )
        
        # Add source information
        for item in headlines:
            item['source'] = source_name
            item['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        return headlines
    
    def scrape_all_sources(self) -> Dict[str, List[Dict]]:
        """
        Scrape headlines from all configured sources
        
        Returns:
            Dictionary with source names as keys and headline lists as values
        """
        results = {}
        
        for source_name, source_config in self.config.SOURCES.items():
            try:
                headlines = self.scrape_source(source_name, source_config)
                results[source_name] = headlines
                # Be respectful - delay between requests
                time.sleep(2)
            except Exception as e:
                logger.error(f"Failed to scrape {source_name}: {e}")
                results[source_name] = []
        
        return results
