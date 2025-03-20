# TRIWA Image Processor

This script processes a CSV file containing TRIWA product variant IDs, fetches product data from the Footway API, extracts image URLs, and adds them to a new CSV file with separate columns for each image.

## Features

- Reads variant IDs from a CSV file
- Makes API calls to fetch product data
- Extracts image URLs from the API response
- Creates a new CSV file with separate columns for each image URL (image_url_1, image_url_2, etc.)
- Optimizes API calls by first determining the maximum number of images per product

## Requirements

- Python 3.6+
- Required packages: `requests`

## Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Ensure your CSV file is in the `data/` directory and named `triwa.csv`
2. Run the script:
   ```
   python hello.py
   ```
3. The script will:
   - First scan all products to determine the maximum number of images
   - Create a new CSV file `data/triwa_with_images.csv` with additional columns for each image URL

## CSV Format

The input CSV file should have at least a `variant_id` column. The output CSV will have all the original columns plus additional columns named `image_url_1`, `image_url_2`, etc., up to the maximum number of images found (capped at 10 by default).

## Notes

- The script includes a small delay between API calls to avoid overwhelming the server
- The script makes two passes through the data: first to count images, then to add the URLs
- Errors during API calls are logged but don't stop the script
- The maximum number of image columns is capped at 10 by default (can be adjusted in the code)
