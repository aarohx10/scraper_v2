# Office Document Scraper

This tool performs web searches and extracts content from websites and office documents (PDF, TXT, DOCX, XLSX, PPTX, etc.) based on search queries.

## Features

- Searches Google for a given query
- Extracts text content from search result pages
- Finds downloadable files (PDF, TXT, Office documents) on those pages
- Extracts text from:
  - PDF files
  - Text files
  - Word documents (DOCX)
  - Excel spreadsheets (XLSX)
  - PowerPoint presentations (PPTX)
- Cleans and processes the text
- Saves results to a JSON file

## Requirements

- Python 3.8+
- Playwright (for web browsing)
- PyMuPDF (for PDF processing)
- python-docx (for DOCX processing)
- openpyxl (for XLSX processing)
- python-pptx (for PPTX processing)
- Beautiful Soup 4 (for HTML parsing)
- Requests (for HTTP requests)

## Quick Start (Recommended)

The easiest way to use the scraper is with Docker and the provided script:

### On Linux/Mac:

1. Make sure Docker and Docker Compose are installed on your system
2. Run the script with your search query:
   ```
   chmod +x run_scraper.sh
   ./run_scraper.sh "your search query here" 15 results.json
   ```
   
   Arguments (all optional):
   - First argument: Search query (default: "site:gov climate change report")
   - Second argument: Number of results to process (default: 10)
   - Third argument: Output file name (default: output.json)

### On Windows:

1. Make sure Docker and Docker Compose are installed on your system
2. Run the batch file with your search query:
   ```
   run_scraper.bat "your search query here" 15 results.json
   ```
   
   Arguments (all optional):
   - First argument: Search query (default: "site:gov climate change report")
   - Second argument: Number of results to process (default: 10)
   - Third argument: Output file name (default: output.json)

## Installation

### Using Docker

1. Make sure Docker is installed on your system
2. Build the Docker image:
   ```
   docker build -t office-scraper .
   ```
3. Run the container:
   ```
   # On Linux/Mac:
   docker run --rm -v $(pwd):/app office-scraper "your search query here"
   
   # On Windows:
   docker run --rm -v %cd%:/app office-scraper "your search query here"
   ```
   The results will be saved to `output.json` in your current directory.

### Using Docker Compose

1. Make sure Docker and Docker Compose are installed on your system
2. Run with environment variables:
   ```
   # On Linux/Mac:
   QUERY="your search query" RESULTS=15 OUTPUT=results.json docker-compose up --build
   
   # On Windows (Command Prompt):
   set QUERY=your search query
   set RESULTS=15
   set OUTPUT=results.json
   docker-compose up --build
   
   # On Windows (PowerShell):
   $env:QUERY="your search query"; $env:RESULTS=15; $env:OUTPUT="results.json"; docker-compose up --build
   ```

### Manual Installation

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Install Playwright browsers:
   ```
   playwright install chromium
   ```
3. Run the script:
   ```
   python office_scraper.py "your search query here"
   ```

## Usage

```
python office_scraper.py [search query] [options]
```

### Options

- `--results N`: Number of search results to process (default: 10)
- `--output FILE`: Output JSON file path (default: output.json)

### Examples

```
# Default search
python office_scraper.py "site:gov climate change report"

# Specify number of results and output file
python office_scraper.py "financial reports 2023" --results 20 --output finance_data.json
```

### Docker Examples

```
# Basic search
docker run --rm -v $(pwd):/app office-scraper "climate change report"

# With options
docker run --rm -v $(pwd):/app office-scraper "financial reports 2023" --results 20 --output finance_data.json
```

## Output Format

The output is a JSON file containing an array of objects, each with the following properties:

- `url`: The URL of the page
- `content`: The extracted content, limited to 10,000 characters

## Limitations

- Only supports modern Office formats (DOCX, XLSX, PPTX)
- Legacy Office formats (DOC, XLS, PPT) are detected but not processed
- Google search results may be limited by Google's rate limiting and bot detection
- Some websites may block scraping attempts 

# Company Research API

A FastAPI-based web service that provides company research capabilities through web scraping.

## Features

- Accepts POST requests with search queries
- Returns cleaned and formatted research results
- Built with FastAPI for high performance
- Deployed with Gunicorn and Nginx
- Systemd service for process management

## API Endpoints

### POST /research
Accepts a JSON payload with a search query and returns research results.

Example request:
```bash
curl -X POST "http://your-server/research" \
     -H "Content-Type: application/json" \
     -d '{"query": "Company Name"}'
```

Example response:
```json
{
    "status": "success",
    "query": "Company Name",
    "result": "Cleaned and formatted research results..."
}
```

### GET /health
Health check endpoint to verify service status.

## Deployment on Hetzner

1. Clone the repository to your Hetzner server:
```bash
git clone <repository-url> /root/company-research
cd /root/company-research
```

2. Make the deployment script executable:
```bash
chmod +x deploy.sh
```

3. Run the deployment script:
```bash
./deploy.sh
```

The script will:
- Install required system packages
- Set up Python virtual environment
- Install dependencies
- Configure and start the service
- Set up Nginx as a reverse proxy

## Service Management

- Start the service: `systemctl start company-research`
- Stop the service: `systemctl stop company-research`
- Restart the service: `systemctl restart company-research`
- View logs: `journalctl -u company-research`

## Environment Variables

No environment variables are required for basic operation. The service is configured to run on port 8000 behind Nginx.

## Security Considerations

- The service runs as root (as required for Playwright)
- Nginx is configured as a reverse proxy
- CORS is enabled for all origins (modify in app.py for production)

## Troubleshooting

1. Check service status:
```bash
systemctl status company-research
```

2. View application logs:
```bash
journalctl -u company-research -f
```

3. Check Nginx configuration:
```bash
nginx -t
```

4. View Nginx logs:
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
``` 