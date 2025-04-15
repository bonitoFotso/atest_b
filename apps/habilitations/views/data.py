# data.py
import pandas as pd


def load_data_from_excel(file_path):
    # Charger le fichier Excel
    df = pd.read_excel(file_path)

    # Créer une liste pour stocker les données de chaque ligne
    all_data = []

    # Parcourir chaque ligne du DataFrame
    for index, row in df.iterrows():
        data = {
            "nom_prenom": {
                "valeur": row['Nom et Prénom'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": 0,
                "couleur": "black"
            },
            "fonction": {
                "valeur": row['Fonction'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -20,
                "couleur": "black"
            },
            "add": {
                "valeur": row['Adresse Entreprise'],
                "taille_police": 25,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": 0,
                "couleur": "black"
            },
            "add2": {
                "valeur": row['Adresse Entreprise 2'],
                "taille_police": 23,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "training_duration": {
                "valeur": row['Durée de Formation'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 8,
                "offset_y": -4,
                "couleur": "black"
            },
            "date": {
                "valeur": row['Date'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": -4,
                "offset_y": -6,
                "couleur": "black"
            },
            "ref": {
                "valeur": row['Référence'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": +6,
                "couleur": "black"
            },
            "symbols": {
                "valeur": row['Symboles'],
                "taille_police": 25,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "titre": {
                "valeur": row['Titre'],
                "taille_police": 30,
                "align": "center",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "#1f66aa"
            },
            "lieu": {
                "valeur": row['Lieu'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "nom": {
                "valeur": row['Nom'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "prenom": {
                "valeur": row['Prénom'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "fonction2": {
                "valeur": row['Fonction 2'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 0,
                "offset_y": -10,
                "couleur": "black"
            },
            "nom_emp": {
                "valeur": row['Nom Employeur'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "prenom_emp": {
                "valeur": row['Prénom Employeur'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "fonction_emp": {
                "valeur": row['Fonction Employeur'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -10,
                "couleur": "black"
            },
            "ref_emp": {
                "valeur": row['Référence Employeur'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "date_emp": {
                "valeur": row['Date Employeur'],
                "taille_police": 20,
                "align": "center",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "validiter": {
                "valeur": row['Validité'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "n_titre": {
                "valeur": row['Numéro de Titre'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "instalations_conserner": {
                "valeur": row['Installations Concernées'],
                "taille_police": 20,
                "align": "center",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "indication": {
                "valeur": row['Indications'],
                "taille_police": 20,
                "align": "center",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "Logo": {
                "valeur": row['Logo'],
                "align": "top_left",
                "offset_x": 0,
                "offset_y": 0,
                "couleur": None
            },
            "Photo": {
                "valeur": row['Photo'],
                "align": "center",
                "offset_x": 0,
                "offset_y": 0,
                "couleur": None
            },
            "QR Code": {
                "valeur": row['QR Code'],
                "align": "top_left",
                "offset_x": 0,
                "offset_y": 0,
                "couleur": None
            },
            "QR Code 2": {
                "valeur": row['QR Code 2'],
                "align": "top_left",
                "offset_x": 0,
                "offset_y": 0,
                "couleur": None
            },
            "personnel": {
                "valeur": row['Personnel'],
                "taille_police": 10,
                "align": "top_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "symbole 2": {
                "valeur": row['Symboles 2'],
                "taille_police": 10,
                "align": "top_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "domaine": {
                "valeur": row['Domaine de tension'],
                "taille_police": 10,
                "align": "top_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
        }

        # Ajouter l'entrée pour cette ligne dans la liste
        all_data.append(data)

    return all_data
