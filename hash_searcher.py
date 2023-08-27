import re
import os
import json
from download_files import download_images_from_json_file
SYSTEM_ID = None


def set_system_id(system_id):
    """Set the global system ID."""
    global SYSTEM_ID
    SYSTEM_ID = system_id


def search_game_by_hash(db, hash_value, game_name, system_id):
    """Search for a game in HFSDB by its hash value."""
    endpoint = f"https://db.hfsplay.fr/api/v1/games?medias__crc32={hash_value}"
    response = db.s.get(endpoint)  # Assuming db.s is the session with authentication

    if response.status_code == 200:
        game_data = response.json()
        if game_data["count"] == 0:  # If no game found by hash, search by name
            print(f"{game_name} not found with hash {hash_value}.")
            game_data = search_game_by_name(db, game_name, system_id)
            if game_data:
                print(f"{game_name} non trouvé, recherche par nom...")
        else:
            json_filename = f"{game_name}.json"
            save_to_json(game_data, f"{game_name}.json")
            download_images_from_json_file(json_filename)
            return game_data
    else:
        print(f"Error searching game with hash {hash_value}. Status code: {response.status_code}")
        print("Response content:", response.text)
        return None


def search_game_by_name(db, name, system_id):
    # Remove file extension
    game_name = os.path.splitext(name)[0]

    # Remove anything between parentheses
    game_name = re.sub(r'\(.*?\)', '', game_name).strip()

    """Search for a game in HFSDB by its name."""
    endpoint = f"https://db.hfsplay.fr/api/v1/games?search={game_name}&system={system_id}"
    response = db.s.get(endpoint)  # Assuming db.s is the session with authentication

    if response.status_code == 200:
        game_data = response.json()

        if game_data["count"] == 0 and '-' in game_name:  # If not found and name contains a hyphen
            # Replace hyphen with colon and try again
            game_name_colon = game_name.replace(' - ', ': ')
            endpoint = f"https://db.hfsplay.fr/api/v1/games?search={game_name_colon}&system={system_id}"
            response = db.s.get(endpoint)

            if response.status_code == 200:
                game_data = response.json()
                if game_data["count"] != 0:  # If found with the colon replacement
                    json_filename = f"{game_name}.json"
                    save_to_json(game_data, f"{game_name_colon}.json")
                    download_images_from_json_file(json_filename)
                    return game_data

        # If found with the original name or not found at all after the colon replacement

        save_to_json(game_data, f"{game_name}.json")
        return game_data

    else:
        print(f"Error searching game with name {game_name}. Status code: {response.status_code}")
        print("Response content:", response.text)
        return None


def save_to_json(data, filename):
    """Save data to a JSON file."""
    with open(filename, 'w') as file:
        json.dump(data, file)
