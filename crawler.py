"""
Web Crawler Module for Documentation Intelligence System
Handles URL crawling, content extraction, and hierarchy preservation
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import logging
from typing import Dict, List, Set, Optional
import validators
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentationCrawler:
    """Crawls documentation websites and extracts structured content"""
    
    def __init__(self, max_depth: int = 3, max_pages: int = 50, delay: float = 1.0):
        """
        Initialize the crawler
        
        Args:
            max_depth: Maximum depth for recursive crawling
            max_pages: Maximum number of pages to crawl
            delay: Delay between requests in seconds
        """
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def validate_url(self, url: str) -> bool:
        """Validate if URL is properly formatted"""
        return validators.url(url) is True
    
    def is_same_domain(self, url: str, base_url: str) -> bool:
        """Check if URL belongs to the same domain as base URL"""
        return urlparse(url).netloc == urlparse(base_url).netloc
    
    def is_documentation_link(self, url: str, base_url: str) -> bool:
        """
        Determine if a link is likely a documentation page
        Filter out non-documentation links like downloads, images, etc.
        """
        url_lower = url.lower()
        
        # Exclude common non-documentation patterns
        excluded_patterns = [
            '.pdf', '.zip', '.exe', '.dmg', '.png', '.jpg', '.jpeg', '.gif',
            '.css', '.js', 'javascript:', 'mailto:', '#', 'download',
            '/api/v', '/login', '/signup', '/register', '/logout'
        ]
        
        for pattern in excluded_patterns:
            if pattern in url_lower:
                return False
        
        # Must be same domain
        if not self.is_same_domain(url, base_url):
            return False
        
        return True
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from URL with retry logic
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content or None if failed
        """
        try:
            response = self.session.get(url, timeout=10, allow_redirects=True)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return None
    
    def extract_content(self, html: str, url: str) -> Dict:
        """
        Extract meaningful content from HTML, excluding navigation and boilerplate
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dictionary with extracted content and metadata
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove script, style, header, footer, nav elements
        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'iframe']):
            tag.decompose()
        
        # Extract title
        title = soup.find('h1')
        if title:
            title = title.get_text(strip=True)
        else:
            title = soup.title.string if soup.title else "Untitled"
        
        # Extract main content
        # Try to find main content area
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=['content', 'main-content', 'documentation'])
        
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return {"title": title, "url": url, "sections": [], "links": []}
        
        # Extract structured sections
        sections = []
        current_section = None
        
        for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'table']):
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # New section
                if current_section:
                    sections.append(current_section)
                
                current_section = {
                    'level': int(element.name[1]),
                    'heading': element.get_text(strip=True),
                    'content': []
                }
            elif current_section:
                # Add content to current section
                text = element.get_text(strip=True)
                if text and len(text) > 10:  # Filter out very short snippets
                    current_section['content'].append(text)
        
        # Add last section
        if current_section:
            sections.append(current_section)
        
        # Extract internal links
        links = []
        for a_tag in main_content.find_all('a', href=True):
            href = a_tag['href']
            absolute_url = urljoin(url, href)
            if self.is_documentation_link(absolute_url, url):
                links.append(absolute_url)
        
        return {
            'title': title,
            'url': url,
            'sections': sections,
            'links': list(set(links))  # Remove duplicates
        }
    
    def crawl(self, start_url: str) -> List[Dict]:
        """
        Crawl documentation starting from a given URL
        
        Args:
            start_url: Starting URL for crawling
            
        Returns:
            List of extracted content from all pages
        """
        if not self.validate_url(start_url):
            logger.error(f"Invalid URL: {start_url}")
            return []
        
        logger.info(f"Starting crawl from: {start_url}")
        
        # Queue for BFS crawling: (url, depth)
        queue = [(start_url, 0)]
        results = []
        
        while queue and len(self.visited_urls) < self.max_pages:
            url, depth = queue.pop(0)
            
            # Skip if already visited or max depth reached
            if url in self.visited_urls or depth > self.max_depth:
                continue
            
            self.visited_urls.add(url)
            logger.info(f"Crawling ({len(self.visited_urls)}/{self.max_pages}): {url}")
            
            # Fetch and parse page
            html = self.fetch_page(url)
            if not html:
                continue
            
            # Extract content
            content = self.extract_content(html, url)
            results.append(content)
            
            # Add linked pages to queue
            if depth < self.max_depth:
                for link in content['links']:
                    if link not in self.visited_urls:
                        queue.append((link, depth + 1))
            
            # Respect rate limiting
            time.sleep(self.delay)
        
        logger.info(f"Crawl complete. Processed {len(results)} pages.")
        return results
    
    def crawl_multiple(self, urls: List[str]) -> Dict[str, List[Dict]]:
        """
        Crawl multiple documentation URLs
        
        Args:
            urls: List of starting URLs
            
        Returns:
            Dictionary mapping each URL to its crawled content
        """
        results = {}
        
        for url in urls:
            logger.info(f"\n{'='*60}\nCrawling: {url}\n{'='*60}")
            self.visited_urls.clear()  # Reset for each new domain
            results[url] = self.crawl(url)
        
        return results
