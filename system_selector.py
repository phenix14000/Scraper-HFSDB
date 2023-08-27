import json


def select_system_by_name():
    # Charger la liste des systèmes à partir du fichier JSON
    with open("systems_list.json", "r") as f:
        systems = json.load(f)

    # Demander à l'utilisateur le nom du système
    search_name = input("Entrez le nom du système (par exemple, PlayStation) : ").strip().lower()

    # Trouver les systèmes correspondants
    matching_systems = [(list(system.keys())[0], list(system.values())[0]) for system in systems if search_name in list(system.values())[0].lower()]

    # Si aucun système correspondant n'est trouvé
    if not matching_systems:
        print("Aucun système correspondant trouvé.")
        return

    # Afficher les systèmes correspondants
    for idx, (system_id, system_name) in enumerate(matching_systems, start=1):
        print(f"{idx}. {system_name}")

    # Demander à l'utilisateur de choisir un système
    while True:
        try:
            choice = int(input("Choisissez un système en entrant un nombre (par exemple, 1, 2, 3, etc.) : "))
            if 1 <= choice <= len(matching_systems):
                break
            else:
                print("Choix non valide. Veuillez choisir un nombre dans la liste.")
        except ValueError:
            print("Veuillez entrer un nombre valide.")

    # Afficher l'ID du système choisi
    selected_system_id, selected_system_name = matching_systems[choice-1]
    print(f"Vous avez choisi : {selected_system_name}. ID du système : {selected_system_id}")
    print(f"Selected System ID: {selected_system_id}")
    return selected_system_id
