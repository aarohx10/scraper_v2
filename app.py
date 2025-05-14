from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from terminal_scraper import main as scraper_main
import asyncio
import re

app = FastAPI(title="Company Research API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchQuery(BaseModel):
    query: str

def clean_output(text):
    """Clean the output by removing unwanted characters and formatting."""
    # Remove asterisks
    text = re.sub(r'\*+', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove empty lines
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()

@app.post("/research")
async def research_company(query: SearchQuery):
    try:
        # Run the existing scraper
        result = await scraper_main(query.query)
        
        # Clean and format the output
        cleaned_result = clean_output(result)
        
        return {
            "status": "success",
            "query": query.query,
            "result": cleaned_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 