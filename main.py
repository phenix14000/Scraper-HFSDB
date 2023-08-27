import os
from hfsdb import HFSDB
from system_selector import select_system_by_name
from hash_searcher import set_system_id
from hash_calculator import compute_hashes
from hash_searcher import search_game_by_hash
from settings import LOGIN, PASSWORD


def login():
    db = HFSDB()
    db.dburl = "https://db.hfsplay.fr/"
    db.login(LOGIN, PASSWORD)
    print(db.account())

    # Appeler la fonction "search_game..."
    system_id = select_system_by_name()
    set_system_id(system_id)  # Set the system ID for hash searching
    directory = input("Please specify the directory to scan: ")
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            file_hashes = compute_hashes(file_path)
            print(f"Hashes for {file}: {file_hashes}")

            # Search for the game by CRC32 hash and filename if not found by hash
            game_info = search_game_by_hash(db, file_hashes["crc32"], file, system_id)

            if game_info:
                print(f"Game info for {file}: {game_info}")
                # Continue with the rest of your code
            else:
                print(f"Game not found for hash {file_hashes['crc32']} and file name {file}")


if __name__ == '__main__':
    login()


