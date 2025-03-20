import csv
import requests
import time

def main():
    # Path to the input and output CSV files
    input_csv_path = 'data/triwa.csv'
    output_csv_path = 'data/triwa_with_images.csv'
    
    # Maximum number of images to handle
    max_images = 20
    
    # First pass: determine the maximum number of images per product
    max_images_found = 0
    variant_image_counts = {}
    
    print("First pass: Counting maximum number of images per product...")
    with open(input_csv_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            variant_id = row['variant_id']
            print(f"Checking image count for variant ID: {variant_id}")
            
            # Make API call to get variant data
            api_url = f"https://prat.i.footway.com/variants/{variant_id}"
            try:
                response = requests.get(api_url)
                response.raise_for_status()
                variant_data = response.json()
                
                # Count images
                image_count = 0
                if 'product' in variant_data and 'attributes' in variant_data['product'] and 'images' in variant_data['product']['attributes']:
                    image_count = len(variant_data['product']['attributes']['images'])
                
                variant_image_counts[variant_id] = image_count
                max_images_found = max(max_images_found, image_count)
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data for variant ID {variant_id}: {e}")
                variant_image_counts[variant_id] = 0
            
            # Add a small delay to avoid overwhelming the API
            time.sleep(0.5)
    
    # Cap the maximum number of images to avoid too many columns
    max_images = min(max_images_found, max_images)
    print(f"Maximum number of images found: {max_images_found}, using {max_images} columns")
    
    # Read the input CSV file again for the second pass
    with open(input_csv_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        # Get the fieldnames from the reader
        fieldnames = reader.fieldnames.copy()
        
        # Add columns for each image URL
        for i in range(1, max_images + 1):
            fieldnames.append(f'image_url_{i}')
        
        # Prepare the output CSV file
        with open(output_csv_path, 'w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Process each row in the CSV
            for row in reader:
                variant_id = row['variant_id']
                print(f"Processing variant ID: {variant_id}")
                
                # If we already know this variant has no images, skip the API call
                if variant_id in variant_image_counts and variant_image_counts[variant_id] == 0:
                    # Initialize all image URL columns to empty
                    for i in range(1, max_images + 1):
                        row[f'image_url_{i}'] = ''
                    writer.writerow(row)
                    continue
                
                # Make API call to get variant data
                api_url = f"https://prat.i.footway.com/variants/{variant_id}"
                try:
                    response = requests.get(api_url)
                    response.raise_for_status()
                    variant_data = response.json()
                    
                    # Extract image URLs from the response
                    image_urls = []
                    if 'product' in variant_data and 'attributes' in variant_data['product'] and 'images' in variant_data['product']['attributes']:
                        for image in variant_data['product']['attributes']['images']:
                            if 'url' in image:
                                image_url = image['url']
                                image_urls.append(image_url)
                    
                    # Add each image URL to its own column
                    for i in range(1, max_images + 1):
                        if i <= len(image_urls):
                            row[f'image_url_{i}'] = image_urls[i-1]
                        else:
                            row[f'image_url_{i}'] = ''
                    
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching data for variant ID {variant_id}: {e}")
                    # Initialize all image URL columns to empty
                    for i in range(1, max_images + 1):
                        row[f'image_url_{i}'] = ''
                
                # Write the row to the output CSV
                writer.writerow(row)
                
                # Add a small delay to avoid overwhelming the API
                time.sleep(0.5)
    
    print(f"Processing complete. Output saved to {output_csv_path}")

if __name__ == "__main__":
    main()
