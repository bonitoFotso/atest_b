# data.py
import pandas as pd

from apps.certifications.views.symbole import organize_by_roles

symbols_to_analyze = ["B0", "H0", "H0V", "B1", "B1V", "B2", "B2V", "B2V Essais",
                      "BC", "BR", "BE", "H1", "H1V", "H2", "H2V", "H2V Essais", "HC"]


def load_data_from_excel(file_path):
    # Charger le fichier Excel
    df = pd.read_excel(file_path)

    # Créer une liste pour stocker les données de chaque ligne
    all_data = []

    # Parcourir chaque ligne du DataFrame
    for index, row in df.iterrows():
        symbols = [symbol for symbol in symbols_to_analyze if row.get(f"{symbol}", "") == "APTE"]
        roles_results = organize_by_roles(symbols)
        roles_list = "\n".join([role for role in roles_results.keys()])
        symbols = ", ".join(sorted(set(symbol for details in roles_results.values() for symbol in details['symbole'])))
        symbols2 = "\n".join([", ".join(details['symbole']) for details in roles_results.values()])
        tensions = "\n".join([", ".join(details['tension']) for details in roles_results.values()])
        periode = f"du {row['Date début']} au {row['Date fin']}" if not pd.isnull(row['Date début']) and not pd.isnull(row['Date fin']) else ""



        data = {
            "Role": {
                "valeur": roles_list,
                "taille_police": 11,
                "align": "top_left",
                "offset_x": 5,
                "offset_y": 0,
                "couleur": "black"
            },
            "Symbole 2": {
                "valeur": symbols2,
                "taille_police": 11,
                "align": "top_left",
                "offset_x": 15,
                "offset_y": 0,
                "couleur": "black"
            },
            "Tension": {
                "valeur": tensions,
                "taille_police": 11,
                "align": "top_left",
                "offset_x": 50,
                "offset_y": 0,
                "couleur": "black"
            },
            "Nom": {
                "valeur": row['Nom'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },

            "Prénom": {
                "valeur": row['Prénom'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "TEL": {
                "valeur": row['TEL'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "BP": {
                "valeur": row['BP'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "Periode": {
                "valeur": periode,
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -15,
                "couleur": "black"
            },

            "Fonction": {
                "valeur": row['Fonction'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "Client": {
                "valeur": row['Client'],
                "taille_police": 25,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": 0,
                "couleur": "black"
            },
            "Employeur 2": {
                "valeur": row['Client'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "Lieu Formations": {
                "valeur": row['Lieu Formations'],
                "taille_police": 23,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "Durée": {
                "valeur": row['Durée de Formation'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 8,
                "offset_y": -4,
                "couleur": "black"
            },
            "Date Remise": {
                "valeur": row['Date'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 6,
                "offset_y": -8,
                "couleur": "black"
            },
            "Référence": {
                "valeur": row['Référence'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "Symboles": {
                "valeur": symbols,
                "taille_police": 25,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "Titre": {
                "valeur": row['Titre'],
                "taille_police": 30,
                "align": "center",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "#1f66aa"
            },
            "Lieu": {
                "valeur": row['Lieu'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 0,
                "offset_y": -10,
                "couleur": "black"
            },
            "Nom 2": {
                "valeur": row['Nom'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "Prénom 2": {
                "valeur": row['Prénom'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "Fonction 2": {
                "valeur": row['Fonction 2'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 0,
                "offset_y": -10,
                "couleur": "black"
            },
            "Nom Emp": {
                "valeur": row['Nom Employeur'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "Prénom Emp": {
                "valeur": row['Prénom Employeur'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "Fonction Emp": {
                "valeur": row['Fonction Employeur'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -5,
                "couleur": "black"
            },
            "Référence 2": {
                "valeur": row['Référence Employeur'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "Date": {
                "valeur": row['Date Employeur'],
                "taille_police": 20,
                "align": "center",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "Validité": {
                "valeur": row['Validité'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "N Titre": {
                "valeur": row['Numéro de Titre'],
                "taille_police": 20,
                "align": "center_vertical_left",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "Installations concernées": {
                "valeur": row['Installations Concernées'],
                "taille_police": 20,
                "align": "center",
                "offset_x": 5,
                "offset_y": -6,
                "couleur": "black"
            },
            "Indication supplémentaire": {
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
            "QR": {
                "valeur": row['QR Code'],
                "align": "top_left",
                "offset_x": 0,
                "offset_y": 0,
                "couleur": None
            },
            "QR 2": {
                "valeur": row['QR Code 2'],
                "align": "top_left",
                "offset_x": 0,
                "offset_y": 0,
                "couleur": None
            }
        }

        # Ajouter l'entrée pour cette ligne dans la liste
        all_data.append(data)

    return all_data
