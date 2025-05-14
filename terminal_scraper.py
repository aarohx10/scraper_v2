import asyncio
import json
import re
import requests
from urllib.parse import urlparse, urljoin, quote_plus
from bs4 import BeautifulSoup
import time
import random
import sys
import socket

def google_search_urls(query, num_results=20):
    """Scrape Google search results for a query using requests."""
    print(f"Searching the web for: {query}")
    
    # Extract company and website from query
    company_name = None
    website = None
    
    # Extract website if present
    website_match = re.search(r'www\.[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', query)
    if website_match:
        website = website_match.group(0)
        # Try to extract company name from parts before the website
        parts = query.split(website)
        if parts[0].strip():
            company_name = parts[0].strip().rstrip(',')
    else:
        # If no website, assume entire query is company name
        company_name = query
        
    print(f"Detected company: {company_name}")
    print(f"Detected website: {website}")
    
    urls = []
    
    # 1. Try the website directly if provided
    if website:
        if not website.startswith('http'):
            website_url = f"https://{website}"
        else:
            website_url = website
            
        urls.append(website_url)
        
        # Add common subpages
        for path in ['', '/about', '/about-us', '/company', '/team', '/contact', '/products', 
                     '/services', '/blog', '/news', '/careers', '/jobs']:
            if path == '' and website_url in urls:
                continue
            urls.append(f"{website_url}{path}")
    
    # 2. Add LinkedIn search for the company
    if company_name:
        urls.append(f"https://www.linkedin.com/company/{company_name.lower().replace(' ', '-')}")
        urls.append(f"https://www.linkedin.com/search/results/companies/?keywords={quote_plus(company_name)}")
    
    # 3. Add other common places to find company info
    if company_name:
        for site in ['crunchbase.com', 'bloomberg.com', 'zoominfo.com', 'glassdoor.com', 
                     'hoovers.com', 'owler.com', 'indeed.com', 'angel.co']:
            urls.append(f"https://www.google.com/search?q={quote_plus(company_name)}+site:{site}")
    
    # 4. Search for news about the company
    if company_name:
        urls.append(f"https://www.google.com/search?q={quote_plus(company_name)}+news")
        urls.append(f"https://www.google.com/search?q={quote_plus(company_name)}+press+release")
    
    # 5. Check for social media presence
    if company_name:
        for social in ['twitter.com', 'facebook.com', 'instagram.com', 'youtube.com']:
            if website:
                company_handle = website.split('.')[1]
                urls.append(f"https://{social}/{company_handle}")
            else:
                company_handle = company_name.lower().replace(' ', '')
                urls.append(f"https://{social}/{company_handle}")
    
    # 6. Search for company reviews
    if company_name:
        urls.append(f"https://www.google.com/search?q={quote_plus(company_name)}+reviews")
        urls.append(f"https://www.google.com/search?q={quote_plus(company_name)}+ratings")
    
    # Remove duplicates and limit results
    urls = list(dict.fromkeys(urls))
    
    return urls[:num_results]

def is_valid_url(url):
    """Check if a URL is valid and reachable."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def normalize_url(base_url, url):
    """Convert relative URLs to absolute URLs."""
    if is_valid_url(url):
        return url
    return urljoin(base_url, url)

def crawl_page(url):
    """Extract text from a webpage."""
    print(f"Crawling {url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Referer": "https://www.google.com/"
        }
        
        # Set a reasonable timeout
        response = requests.get(url, timeout=20, headers=headers, allow_redirects=True)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '').lower()
        if not ('text/html' in content_type or 'application/xhtml+xml' in content_type):
            return f"[Not HTML content: {content_type}]"
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract title
        title = soup.title.string if soup.title else "No title"
        
        # Extract meta description
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and meta_tag.get("content"):
            meta_desc = meta_tag["content"]
            
        # Extract text content
        for script in soup(["script", "style"]):
            script.extract()
            
        # Try to get structured content first
        structured_content = ""
        
        # Check for specific content sections
        article = soup.find(['article', 'main'])
        if article:
            structured_content = article.get_text(separator="\n", strip=True)
        
        # If no article/main, look for content divs
        if not structured_content:
            content_divs = soup.find_all(['div', 'section'], class_=lambda c: c and any(x in str(c).lower() for x in ['content', 'main', 'article', 'body']))
            if content_divs:
                for div in content_divs:
                    structured_content += div.get_text(separator="\n", strip=True) + "\n\n"
        
        # If still no content, get all paragraphs
        if not structured_content:
            paragraphs = soup.find_all('p')
            structured_content = "\n\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        # If still nothing, get all text
        if not structured_content:
            structured_content = soup.get_text(separator="\n", strip=True)
        
        # Special handling for LinkedIn
        if 'linkedin.com' in url:
            linkedin_sections = []
            
            # Company overview
            overview = soup.find_all(['section', 'div'], class_=lambda c: c and 'overview' in str(c).lower())
            if overview:
                for section in overview:
                    linkedin_sections.append("COMPANY OVERVIEW:\n" + section.get_text(separator="\n", strip=True))
            
            # About section
            about = soup.find_all(['section', 'div'], class_=lambda c: c and 'about' in str(c).lower())
            if about:
                for section in about:
                    linkedin_sections.append("ABOUT SECTION:\n" + section.get_text(separator="\n", strip=True))
            
            # Employees/people
            people = soup.find_all(['section', 'div'], class_=lambda c: c and 'employee' in str(c).lower() or 'people' in str(c).lower())
            if people:
                for section in people:
                    linkedin_sections.append("EMPLOYEES/PEOPLE:\n" + section.get_text(separator="\n", strip=True))
                    
            if linkedin_sections:
                structured_content = "\n\n".join(linkedin_sections)
        
        # Special handling for review sites
        if any(site in url for site in ['glassdoor.com', 'indeed.com', 'yelp.com']):
            reviews = soup.find_all(['div', 'section'], class_=lambda c: c and 'review' in str(c).lower())
            if reviews:
                reviews_text = []
                for section in reviews:
                    reviews_text.append(section.get_text(separator="\n", strip=True))
                structured_content = "REVIEWS:\n\n" + "\n\n".join(reviews_text)
        
        # Format the final output
        full_content = f"SOURCE: {url}\nTITLE: {title}\nDESCRIPTION: {meta_desc}\n\nFULL CONTENT:\n{structured_content}"
        
        return full_content
        
    except requests.exceptions.RequestException as e:
        print(f"Request error crawling {url}: {e}")
        return f"[Could not retrieve content from {url}: {str(e)}]"
    except Exception as e:
        print(f"Error crawling {url}: {e}")
        return f"[Error processing {url}: {str(e)}]"

async def process_url(url):
    """Process a single URL and extract all relevant information."""
    # Add some random delay to avoid rate limiting
    await asyncio.sleep(random.uniform(0.5, 2.0))
    
    page_text = crawl_page(url)
    
    # Don't trim content for full detailed output
    return {
        "url": url,
        "content": page_text  # No character limit here
    }

async def main(query):
    """Main function to run the scraper and print detailed results to terminal."""
    print(f"Starting comprehensive company research for: {query}")
    
    # Get URLs for the company
    urls = google_search_urls(query, num_results=20)
    
    print(f"Found {len(urls)} URLs to process")
    
    # Process each URL
    tasks = [process_url(url) for url in urls]
    results = await asyncio.gather(*tasks)
    
    # Filter out empty results or error messages only
    results = [r for r in results if r["content"] and not r["content"].startswith("[Could not") and len(r["content"]) > 200]
    
    # Print full detailed results to terminal
    print("\n" + "=" * 100)
    print(f"COMPREHENSIVE DATA FOR: {query}")
    print("=" * 100 + "\n")
    
    for i, result in enumerate(results, 1):
        print(f"DETAILED SOURCE {i}/{len(results)}: {result['url']}")
        print("=" * 100)
        print(result['content'])
        print("\n" + "=" * 100 + "\n")
    
    print(f"Research completed. Found detailed information from {len(results)} sources.")
    
    return results

if __name__ == "__main__":
    # If arguments provided, use them as query
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        # Otherwise prompt for input
        query = input("Enter company name and/or website: ")
    
    if not query:
        print("No query provided. Exiting.")
        sys.exit(1)
    
    print(f"Starting comprehensive research for: {query}")
    asyncio.run(main(query))