import csv
import io
import requests
import time
import os
from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI(title="TRIWA Image API")

def fetch_ean_data(ean: str) -> Dict[str, Any]:
    """Fetch data for a specific EAN from the API."""
    url = f"https://prat.i.footway.com/ean/{ean}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for EAN {ean}: {e}")
        return {}

def extract_image_urls(data: Dict[str, Any]) -> List[str]:
    """Extract image URLs from the API response."""
    images = []
    
    try:
        # Navigate through the nested structure to reach the images array
        if (data and 'variant' in data and 'product' in data['variant'] and 
            'attributes' in data['variant']['product'] and 
            'images' in data['variant']['product']['attributes']):
            
            for image in data['variant']['product']['attributes']['images']:
                if 'url' in image:
                    images.append(image['url'])
    except Exception as e:
        print(f"Error extracting image URLs: {e}")
    
    return images

def process_ean_list(ean_list: List[str]) -> io.StringIO:
    """Process a list of EANs and return a CSV file as StringIO."""
    # Create a StringIO object to store CSV data
    csv_output = io.StringIO()
    
    if not ean_list:
        raise HTTPException(status_code=400, detail="No EANs provided")
    
    print(f"Processing {len(ean_list)} EANs")
    
    # Determine the maximum number of images to prepare columns
    print("First pass: Counting maximum number of images per EAN...")
    max_images = 0
    ean_data_cache = {}
    
    for ean in ean_list:
        print(f"Checking image count for EAN: {ean}")
        data = fetch_ean_data(ean)
        ean_data_cache[ean] = data
        
        image_urls = extract_image_urls(data)
        max_images = max(max_images, len(image_urls))
        
        # Add a small delay to avoid overwhelming the API
        time.sleep(0.5)
    
    print(f"Maximum number of images found: {max_images}")
    
    # Prepare the fieldnames for the CSV
    fieldnames = ['ean']
    for i in range(1, max_images + 1):
        fieldnames.append(f'image_url_{i}')
    
    # Write data to CSV
    writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
    writer.writeheader()
    
    for ean in ean_list:
        print(f"Processing EAN: {ean}")
        row = {'ean': ean}
        
        # Get the data from cache
        data = ean_data_cache.get(ean, {})
        image_urls = extract_image_urls(data)
        
        # Add image URLs to the row
        for i in range(1, max_images + 1):
            if i <= len(image_urls):
                row[f'image_url_{i}'] = image_urls[i-1]
            else:
                row[f'image_url_{i}'] = ''
        
        writer.writerow(row)
    
    # Reset the pointer to the start of the StringIO object
    csv_output.seek(0)
    return csv_output

@app.post("/process-eans/")
async def process_eans_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to process a list of EANs from an uploaded file and return a CSV file with image URLs.
    
    The input file should contain one EAN per line.
    """
    try:
        # Read the uploaded file
        contents = await file.read()
        ean_list = contents.decode('utf-8').splitlines()
        
        # Filter out empty lines
        ean_list = [ean.strip() for ean in ean_list if ean.strip()]
        
        # Process the EAN list
        csv_output = process_ean_list(ean_list)
        
        # Return the CSV file as a downloadable response
        return StreamingResponse(
            iter([csv_output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment;filename=triwa_images.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing EAN list: {str(e)}")

@app.post("/process-eans-text/")
async def process_eans_text(ean_list: List[str]):
    """
    Endpoint to process a list of EANs provided as a JSON array and return a CSV file with image URLs.
    
    The input should be a JSON array of EAN strings.
    Example: ["7350056808765", "7350056806419"]
    """
    try:
        # Filter out empty strings
        ean_list = [ean.strip() for ean in ean_list if ean and ean.strip()]
        
        if not ean_list:
            raise HTTPException(status_code=400, detail="No valid EANs provided")
        
        # Process the EAN list
        csv_output = process_ean_list(ean_list)
        
        # Return the CSV file as a downloadable response
        return StreamingResponse(
            iter([csv_output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment;filename=triwa_images.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing EAN list: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 