import re
import urllib.parse
import hashlib
import logging
from bs4 import BeautifulSoup
import requests
import urllib3

# Suppress SSL verification warnings for local testing / offline setups
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crawler")

class WebCrawler:
    def __init__(self, seed_url, max_depth=2):
        self.seed_url = seed_url
        self.max_depth = max_depth
        self.parsed_seed = urllib.parse.urlparse(seed_url)
        self.base_domain = self.parsed_seed.netloc
        self.visited_urls = set()
        self.content_hashes = set()
        self.results = []

    def normalize_url(self, url):
        """Normalize URL to prevent crawling duplicate links (removes fragments, UTM params, trailing slashes)."""
        parsed = urllib.parse.urlparse(url)
        # Reconstruct without fragment and downcase host
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = parsed.path
        if path.endswith('/') and len(path) > 1:
            path = path[:-1]
        
        # Filter query params, keeping main ones but removing tracking parameters
        query_params = urllib.parse.parse_qsl(parsed.query)
        filtered_params = [
            (k, v) for k, v in query_params 
            if not k.startswith('utm_') and k not in ('fbclid', 'gclid', 'sessionid', 'sid')
        ]
        query = urllib.parse.urlencode(filtered_params)
        
        normalized = urllib.parse.urlunparse((scheme, netloc, path, parsed.params, query, ''))
        return normalized

    def is_internal(self, url):
        """Check if URL belongs to the same domain or subdomain as the seed URL."""
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower()
        # Direct match or subdomain match
        return netloc == self.base_domain or netloc.endswith("." + self.base_domain)

    def should_skip_url(self, url):
        """Filter out logins, signup pages, static assets, ads, or tracking URLs."""
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.lower()
        query = parsed.query.lower()
        full_url = url.lower()

        # Check file extensions to avoid binary assets
        skip_extensions = (
            '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.doc', '.docx', '.zip', 
            '.tar', '.gz', '.mp3', '.mp4', '.avi', '.css', '.js', '.svg', '.woff', '.xml'
        )
        if path.endswith(skip_extensions):
            return True

        # Check keywords for login/signup/ads
        skip_keywords = (
            'login', 'signin', 'signup', 'register', 'logout', 'auth', 
            'password-reset', 'cart', 'checkout', 'adserver', 'doubleclick', 
            'googleads', 'telemetry', 'track'
        )
        for keyword in skip_keywords:
            if keyword in path or keyword in query:
                return True
                
        return False

    def get_content_hash(self, text):
        """Compute SHA256 of text to detect duplicate content."""
        return hashlib.sha256(text.encode('utf-8', errors='ignore')).hexdigest()

    def extract_links(self, soup, current_url):
        """Extract all valid internal links from a page."""
        links = []
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            # Resolve relative URLs
            absolute_url = urllib.parse.urljoin(current_url, href)
            normalized = self.normalize_url(absolute_url)
            
            if self.is_internal(normalized) and not self.should_skip_url(normalized):
                links.append(normalized)
        return list(set(links))

    def parse_page(self, html_content, url):
        """Parse HTML to extract title, metadata, tables, JSON-LD, and paragraph text."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove noisy elements
        for script_or_style in soup(["script", "style", "nav", "footer", "header", "iframe", "noscript"]):
            # Keep JSON-LD scripts for metadata extraction
            if script_or_style.name == 'script' and script_or_style.get('type') == 'application/ld+json':
                continue
            script_or_style.decompose()

        # 1. Metadata Extraction
        title = soup.title.string.strip() if soup.title else ""
        meta_desc = ""
        meta_desc_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if meta_desc_tag:
            meta_desc = meta_desc_tag.get('content', '').strip()

        # 2. JSON-LD Extraction
        json_ld_data = []
        for json_ld_tag in soup.find_all('script', type='application/ld+json'):
            try:
                import json
                data = json.loads(json_ld_tag.string)
                json_ld_data.append(data)
            except Exception:
                pass

        # 3. Table Extraction
        tables = []
        for table_tag in soup.find_all('table'):
            table_rows = []
            for row in table_tag.find_all('tr'):
                cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                if cells:
                    table_rows.append(" | ".join(cells))
            if table_rows:
                tables.append("\n".join(table_rows))
            table_tag.decompose()  # Decompose so table content isn't duplicated in main text

        # 4. Clean Main Text Paragraphs
        chunks = []
        
        # Extract headings and group paragraphs below them
        current_heading = "General"
        paragraphs = []
        
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li']):
            text = element.get_text(strip=True)
            if not text:
                continue
                
            if element.name in ['h1', 'h2', 'h3', 'h4']:
                # Save previous group if it exists
                if paragraphs:
                    combined_text = "\n".join(paragraphs)
                    if len(combined_text) >= 100:  # Low-content filter
                        chunks.append({
                            "text": combined_text,
                            "type": "paragraph",
                            "metadata": {
                                "heading": current_heading,
                                "url": url
                            }
                        })
                    paragraphs = []
                current_heading = text
            else:
                paragraphs.append(text)
                
        # Append final group of paragraphs
        if paragraphs:
            combined_text = "\n".join(paragraphs)
            if len(combined_text) >= 100:
                chunks.append({
                    "text": combined_text,
                    "type": "paragraph",
                    "metadata": {
                        "heading": current_heading,
                        "url": url
                    }
                })

        # Append tables as distinct chunks
        for tbl in tables:
            chunks.append({
                "text": tbl,
                "type": "table",
                "metadata": {
                    "heading": "Table",
                    "url": url
                }
            })

        # Append JSON-LD as a structured chunk if present
        if json_ld_data:
            import json
            chunks.append({
                "text": json.dumps(json_ld_data, indent=2),
                "type": "structured",
                "metadata": {
                    "heading": "Structured Metadata (JSON-LD)",
                    "url": url
                }
            })

        # Generate clean page text representation for duplicate content hashing
        all_text = " ".join([c["text"] for c in chunks])
        content_hash = self.get_content_hash(all_text)
        
        if content_hash in self.content_hashes:
            logger.info(f"Skipping duplicate content page: {url}")
            return None

        self.content_hashes.add(content_hash)
        
        return {
            "source_type": "web",
            "source": url,
            "title": title,
            "description": meta_desc,
            "chunks": chunks
        }

    def crawl_recursive(self, url, depth):
        """Perform recursive breadth-first crawling."""
        normalized = self.normalize_url(url)
        if normalized in self.visited_urls or depth > self.max_depth:
            return

        self.visited_urls.add(normalized)
        logger.info(f"Crawling (Depth {depth}/{self.max_depth}): {normalized}")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
            }
            # Use verify=False to bypass SSL check issues
            response = requests.get(normalized, headers=headers, timeout=10, verify=False)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {normalized}: HTTP {response.status_code}")
                return

            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                logger.info(f"Skipping non-HTML page {normalized}: {content_type}")
                return

            soup = BeautifulSoup(response.text, 'html.parser')
            parsed_data = self.parse_page(response.text, normalized)
            
            if parsed_data:
                self.results.append(parsed_data)

            # Recurse if depth permits
            if depth < self.max_depth:
                next_links = self.extract_links(soup, normalized)
                for link in next_links:
                    self.crawl_recursive(link, depth + 1)

        except Exception as e:
            logger.error(f"Error crawling {normalized}: {e}")

    def crawl(self):
        """Start the crawling process."""
        self.crawl_recursive(self.seed_url, 0)
        return self.results

# Simple verification block
if __name__ == "__main__":
    crawler = WebCrawler("https://example.com", max_depth=1)
    results = crawler.crawl()
    print(f"Crawled {len(results)} pages successfully.")
    if results:
        print("First result title:", results[0]["title"])
        print("Number of chunks in first result:", len(results[0]["chunks"]))
