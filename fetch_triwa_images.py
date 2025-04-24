import csv
import requests
import time
import os
from typing import List, Dict, Any

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

def read_ean_list(input_file: str) -> List[str]:
    """Read the list of EANs from a file.
    
    The file should contain one EAN per line.
    """
    ean_list = []
    try:
        with open(input_file, 'r') as f:
            for line in f:
                # Strip whitespace and skip empty lines
                ean = line.strip()
                if ean:
                    ean_list.append(ean)
        return ean_list
    except Exception as e:
        print(f"Error reading EAN list from file {input_file}: {e}")
        return []

def main():
    # File containing the list of EANs (one per line)
    input_file = 'data/ean_list.txt'
    
    # Output CSV file path
    output_csv_path = 'data/triwa_images.csv'
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Read the list of EANs from the file
    ean_list = read_ean_list(input_file)
    
    if not ean_list:
        print(f"No EANs found in file {input_file}. Exiting.")
        return
    
    print(f"Found {len(ean_list)} EANs in {input_file}")
    
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
    with open(output_csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
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
    
    print(f"Processing complete. Output saved to {output_csv_path}")

if __name__ == "__main__":
    main() 