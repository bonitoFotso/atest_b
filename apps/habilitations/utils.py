import locale
from datetime import datetime


def format_date_range(start_date, end_date):
    """
    Formate une plage de dates pour afficher "du {jour1} au {jour2} {mois} {année}".

    :param start_date: Date de début au format "21 Novembre 2024"
    :param end_date: Date de fin au format "22 Novembre 2024"
    :return: Une chaîne formatée.
    """
    # Définir les paramètres régionaux en français
    try:
        locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
    except locale.Error:
        return "Erreur : Les paramètres régionaux français ne sont pas disponibles sur ce système."

    # Conversion des chaînes de dates en objets datetime
    start = datetime.strptime(start_date, "%d %B %Y")
    end = datetime.strptime(end_date, "%d %B %Y")

    # Vérification de l'année et du mois
    if start.year == end.year and start.month == end.month:
        return f"{start.day} et {end.day} {start.strftime('%B')} {start.year}"
    elif start.year == end.year:
        return f"du {start.day} {start.strftime('%B')} et {end.day} {end.strftime('%B')} {start.year}"
    else:
        return f"du {start.day} {start.strftime('%B')} {start.year} au {end.day} {end.strftime('%B')} {end.year}"


# Exemple d'utilisation
start_date = "21 Novembre 2024"
end_date = "22 Novembre 2024"
result = format_date_range(start_date, end_date)
print(result)  # Affiche: du 21 au 22 Novembre 2024
