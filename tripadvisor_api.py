import json
import http.client
import os
from fastapi import FastAPI, HTTPException
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
async def root():
    return {"message": "Welcome to TourpalCrawler. Use /googletrip?hotel=<hotel>&location=<location> or /tripadvisor?hotel=<hotel>&location=<location>"}

def fetch_images(hotel: str, location: str, api_key: str, source: str) -> list:
    """Fetch images from Serper API for a given source."""
    try:
        conn = http.client.HTTPSConnection("google.serper.dev")
        query = f"{hotel} {location} site:{source}"
        payload = json.dumps({"q": query})
        headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
        conn.request("POST", "/images", payload, headers)
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        conn.close()

        logger.info(f"Serper response for {source}: {data}")

        image_urls = []
        for item in data.get("images", []):
            url = item.get("imageUrl", "")
            if url and url.startswith("http"):
                image_urls.append(url)  # No source filtering, like old code
        
        logger.info(f"Image URLs for {source}: {image_urls}")
        return image_urls
    except Exception as e:
        logger.error(f"{source} API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"{source} API error: {str(e)}")

@app.get("/googletrip")
async def get_google_travel_images(hotel: str, location: str):
    if not hotel or not location:
        raise HTTPException(status_code=400, detail="Hotel and location are required.")
    
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        raise HTTPException(status_code=500, detail="Serper API key not configured.")

    try:
        image_urls = fetch_images(hotel, location, serper_api_key, "google.com/travel")
        return list(set(image_urls))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/tripadvisor")
async def get_tripadvisor_images(hotel: str, location: str):
    if not hotel or not location:
        raise HTTPException(status_code=400, detail="Hotel and location are required.")
    
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        raise HTTPException(status_code=500, detail="Serper API key not configured.")

    try:
        image_urls = fetch_images(hotel, location, serper_api_key, "tripadvisor.com")
        return list(set(image_urls))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)