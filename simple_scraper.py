import asyncio
import json
import re
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def google_search(query, num_results=10):
    """Perform a Google search and return a list of result URLs."""
    urls = []
    print(f"Searching Google for: {query}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        )
        page = await context.new_page()

        # Navigate to Google and perform search
        await page.goto(f"https://www.google.com/search?q={query}", timeout=60000)
        
        # Wait for search results to load
        await page.wait_for_selector("div#search", timeout=10000)
        
        # Extract result links
        result_links = await page.query_selector_all("div.g a[href^='http']")
        
        for link in result_links:
            href = await link.get_attribute("href")
            if href and href.startswith("http"):
                # Filter out Google's own domains
                parsed_url = urlparse(href)
                if "google" not in parsed_url.netloc:
                    urls.append(href)
                    print(f"Found URL: {href}")
            
            if len(urls) >= num_results:
                break
                
        # If we didn't get enough results with the first selector, try another common one
        if len(urls) < num_results:
            elements = await page.query_selector_all("a")
            for e in elements:
                href = await e.get_attribute("href")
                if href and href.startswith("/url?q="):
                    clean_url = href.split("/url?q=")[1].split("&sa=")[0]
                    if not clean_url.startswith("http"):
                        continue
                    
                    parsed_url = urlparse(clean_url)
                    if "google" not in parsed_url.netloc and clean_url not in urls:
                        urls.append(clean_url)
                        print(f"Found URL: {clean_url}")
                
                if len(urls) >= num_results:
                    break

        await browser.close()
    
    return list(set(urls))

def is_valid_url(url):
    """Check if a URL is valid."""
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        }
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract text content
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator=" ", strip=True)
        
        return text
        
    except Exception as e:
        print(f"Error crawling {url}: {e}")
        return ""

def clean_text(text):
    """Clean and normalize extracted text."""
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    
    # Convert None values to empty strings
    text = re.sub(r'None', '', text)
    
    # Remove extra whitespace, newlines, tabs
    text = re.sub(r'\s+', ' ', text)
    
    # Remove very long words (likely garbage)
    text = re.sub(r'\S{50,}', '', text)
    
    return text.strip()

def save_json(data, filename="output.json"):
    """Save the results to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Data saved to {filename}")

async def process_url(url):
    """Process a single URL and extract all relevant information."""
    page_text = crawl_page(url)
    
    # Clean the text
    cleaned_text = clean_text(page_text)
    
    return {
        "url": url,
        "content": cleaned_text[:10000]  # Limit to 10k chars to prevent huge outputs
    }

async def main(query, num_results=10, output_file="output.json"):
    """Main function to run the scraper."""
    print(f"Starting scraper for query: {query}")
    
    # Get URLs from Google search
    urls = await google_search(query, num_results)
    print(f"Found {len(urls)} URLs")
    
    # Process each URL
    tasks = [process_url(url) for url in urls]
    results = await asyncio.gather(*tasks)
    
    # Remove empty results
    results = [r for r in results if r["content"]]
    
    # Save results
    save_json(results, output_file)
    print(f"Scraping completed. Found content from {len(results)} pages.")
    
    return results

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Web Scraper")
    parser.add_argument("query", nargs="*", help="Search query")
    parser.add_argument("--results", type=int, default=10, help="Number of search results to process")
    parser.add_argument("--output", default="output.json", help="Output JSON file")
    
    args = parser.parse_args()
    
    query = " ".join(args.query) if args.query else "site:gov climate change report"
    
    print(f"Starting scraper with query: {query}")
    asyncio.run(main(query, args.results, args.output))
