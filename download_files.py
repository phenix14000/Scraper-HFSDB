import requests
import os
import json


def download_images_from_json_file(json_filename):
    # Load the JSON data from the provided filename
    with open(json_filename, 'r') as file:
        json_data = json.load(file)

    results_data = json_data.get("results", [])

    # Extract available image types and regions
    image_types = list(set(media["type"]
                           for game in results_data
                           for media in game.get("medias", [])
                           if media["is_image"]))
    image_regions = list(set(media["region"]
                             for game in results_data
                             for media in game.get("medias", [])
                             if media["is_image"]))

    print("Debug: Extracted image types and regions.")

    # Get user input for save location, image type, and region
    save_location = input("Enter the directory where you want to save the images: ")
    print("Available image types:", ", ".join(image_types))
    chosen_image_type = input("Enter the image type you want to download (e.g., cover2d, logo): ")
    print("Available regions:", ", ".join([region for region in image_regions if region]))  # exclude None
    chosen_region = input("Enter the region for the images (e.g., WORLD, EU) or press Enter for no specific region: ")

    # Create save directory if it doesn't exist
    if not os.path.exists(save_location):
        os.makedirs(save_location)

    print("Debug: Starting download process...")

    # Download the images
    for game in results_data:
        for media in game.get("medias", []):
            if media["is_image"] and media["type"] == chosen_image_type and (
                    not chosen_region or media["region"] == chosen_region):
                image_url = media["file"]
                print(f"Debug: Trying to download image from {image_url}")
                response = requests.get(image_url, stream=True)
                response.raise_for_status()
                # Create a filename based on the JSON filename and the media ID
                image_filename = os.path.join(save_location,
                                              f"{os.path.splitext(json_filename)[0]}-{media['id']}.{media['extension']}")
                with open(image_filename, 'wb') as img_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        img_file.write(chunk)
                print(f"Downloaded {image_filename}")
            else:
                print(f"Debug: Skipping media with type {media['type']} and region {media['region']}")
