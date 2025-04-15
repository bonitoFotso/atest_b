import json

def merge_json_with_combined_keys(file1_path, file2_path, output_path):
    # Charger les deux fichiers JSON
    with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
        data1 = json.load(file1)
        data2 = json.load(file2)

    # Fusionner les données avec des clés combinées
    merged_data = {}
    for key1, value1 in data1.items():
        found = False
        for key2, value2 in data2.items():
            if value1 == value2:
                found = True
                # Créer une clé combinée pour les valeurs identiques
                combined_key = [key1, key2]
                merged_data[combined_key] = value1
                break
        if not found:
            # Ajouter les données de data1 si elles ne sont pas dans data2
            merged_data[str([key1, "non_correspondant"])] = value1

    # Ajouter les données restantes de data2 qui ne sont pas dans data1
    for key2, value2 in data2.items():
        if not any(value2 == merged_data[key] for key in merged_data):
            merged_data[str(["non_correspondant", key2])] = value2

    # Enregistrer le fichier fusionné
    with open(output_path, 'w') as output_file:
        json.dump(merged_data, output_file, indent=4, ensure_ascii=False)
    print(f"Fusion réussie ! Le fichier fusionné est enregistré à : {output_path}")

# Remplacez les chemins suivants par vos propres fichiers
file1_path = "th.json"  # Chemin vers le premier fichier JSON
file2_path = "th2.json"  # Chemin vers le deuxième fichier JSON
output_path = "coordonne_TH.json"  # Chemin vers le fichier fusionné

# Appeler la fonction de fusion
merge_json_with_combined_keys(file1_path, file2_path, output_path)
