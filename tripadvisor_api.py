import json
import http.client
import os
from fastapi import FastAPI, HTTPException

app = FastAPI()

def get_google_travel_images(hotel: str, location: str, api_key: str) -> list:
    conn = http.client.HTTPSConnection("google.serper.dev")
    query = f"{hotel} {location} site:google.com/travel"
    payload = json.dumps({"q": query})
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    conn.request("POST", "/images", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    conn.close()

    image_urls = []
    for item in data.get("images", []):
        url = item.get("imageUrl", "")
        if url and url.startswith("http"):
            image_urls.append(url)
    
    if not image_urls:
        raise Exception("No images found.")
    return image_urls

@app.get("/images")
async def get_images(hotel: str, location: str):
    if not hotel or not location:
        raise HTTPException(status_code=400, detail="Hotel and location are required.")
    
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        raise HTTPException(status_code=500, detail="Serper API key not configured.")

    try:
        image_urls = get_google_travel_images(hotel, location, serper_api_key)
        return list(set(image_urls))  # Remove duplicates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)