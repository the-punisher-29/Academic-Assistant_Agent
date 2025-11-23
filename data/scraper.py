import os
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from io import BytesIO
from urllib.parse import urljoin, urlparse
import re

# Directory to save extracted data
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# Initial URLs provided
START_URLS = [
    "http://academics.iitj.ac.in/?page_id=377",
    "https://iitj.ac.in/office-of-academics/en/list-of-academic-programs",
    "https://iitj.ac.in/office-of-academics/en/curriculum",
    "https://www.iitj.ac.in/PageImages/Gallery/07-2025/Academic-Calendar-AY-202526SemI2-with-CCCD-events-638871414539740843.pdf"
]

def clean_filename(url):
    """Generate a clean filename from a URL."""
    parsed = urlparse(url)
    path = parsed.path
    if path.endswith('/'):
        path = path[:-1]
    
    name = os.path.basename(path)
    if not name:
        name = "index"
    
    # Add query params if present to distinguish pages
    if parsed.query:
        name += "_" + re.sub(r'[^a-zA-Z0-9]', '_', parsed.query)
        
    # Remove extension if present to add .txt later
    name = os.path.splitext(name)[0]
    
    # Ensure valid filename chars
    name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    return name

def save_content(name, content, source_url):
    """Save extracted content to a text file."""
    filename = f"{name}.txt"
    filepath = os.path.join(DATA_DIR, filename)
    
    header = f"Source: {source_url}\n"
    header += "=" * 80 + "\n\n"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(header + content)
    print(f"Saved: {filename}")

def extract_pdf_text(pdf_content):
    """Extract text from PDF binary content."""
    try:
        with BytesIO(pdf_content) as f:
            reader = PdfReader(f)
            text = []
            for page in reader.pages:
                text.append(page.extract_text())
            return "\n".join(text)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def scrape_url(url, visited=None):
    if visited is None:
        visited = set()
    
    if url in visited:
        return
    visited.add(url)
    
    print(f"Scraping: {url}")
    
    try:
        # Fake user agent to avoid some blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10, verify=False) # verify=False for some academic sites with bad certs
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'application/pdf' in content_type or url.lower().endswith('.pdf'):
            # Handle PDF
            text = extract_pdf_text(response.content)
            name = clean_filename(url)
            if "calendar" in name.lower():
                name = "scraped_academic_calendar"
            save_content(name, text, url)
            
        elif 'text/html' in content_type:
            # Handle HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text(separator='\n')
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = '\n'.join(chunk for chunk in chunks if chunk)
            
            name = clean_filename(url)
            save_content(name, clean_text, url)
            
            # Look for linked PDFs on the page
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                # Only follow PDF links
                if full_url.lower().endswith('.pdf'):
                    scrape_url(full_url, visited)
                    
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")

def main():
    # Suppress SSL warnings for this script
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    visited = set()
    for url in START_URLS:
        scrape_url(url, visited)

if __name__ == "__main__":
    main()
