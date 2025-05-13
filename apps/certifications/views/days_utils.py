from datetime import datetime, timedelta

month_translation = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
    7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
}

def format_date_range(date_debut, date_fin, date_deb_e=None, date_fin_e=None, have_saturday=True, have_sunday=True):
    try:
        # Parse les dates présentielles
        start_date = datetime.strptime(date_debut, "%d/%m/%y")
        end_date = datetime.strptime(date_fin, "%d/%m/%y")
        
        # Parse les dates e-learning si présentes
        start_date_e = datetime.strptime(date_deb_e, "%d/%m/%y") if date_deb_e else None
        end_date_e = datetime.strptime(date_fin_e, "%d/%m/%y") if date_fin_e else None

        def calculate_working_days(start, end, include_saturday=True, include_sunday=True):
            if not start or not end:
                return []
            total_days = []
            current_date = start
            while current_date <= end:
                if current_date.weekday() == 5 and not include_saturday:
                    current_date += timedelta(days=1)
                    continue
                if current_date.weekday() == 6 and not include_sunday:
                    current_date += timedelta(days=1)
                    continue
                total_days.append(current_date)
                current_date += timedelta(days=1)
            return total_days

        # Calculer les jours effectifs
        working_days = calculate_working_days(start_date, end_date, have_saturday, have_sunday)
        working_days_e = calculate_working_days(start_date_e, end_date_e, have_saturday, have_sunday)

        if working_days:
            start_date = working_days[0]
            end_date = working_days[-1]
            duration_days = len(working_days)
        else:
            duration_days = 0

        if working_days_e:
            start_date_e = working_days_e[0]
            end_date_e = working_days_e[-1]
            duration_days_e = len(working_days_e)
        else:
            duration_days_e = 0

        def format_period(start, end):
            if not start or not end:
                return ""
            if start == end:
                return f"{start.day} {month_translation[start.month]} {start.year}"
            elif start.month == end.month and start.year == end.year:
                return f"{start.day} au {end.day} {month_translation[start.month]} {start.year}"
            elif start.year == end.year:
                return f"{start.day} {month_translation[start.month]} au {end.day} {month_translation[end.month]} {start.year}"
            else:
                return f"{start.day} {month_translation[start.month]} {start.year} au {end.day} {month_translation[end.month]} {end.year}"

        # Formater les périodes
        period_pres = {
            'start': start_date,
            'end': end_date,
            'formatted': format_period(start_date, end_date),
            'type': 'présentiel'
        }

        period_e = {
            'start': start_date_e,
            'end': end_date_e,
            'formatted': format_period(start_date_e, end_date_e),
            'type': 'e-learning'
        } if start_date_e and end_date_e else None

        # Trier les périodes chronologiquement
        periods = [period_pres]
        if period_e:
            periods.append(period_e)
        
        periods.sort(key=lambda x: x['start'])
        
        # Construire la chaîne formatée finale
        formatted_date = periods[0]['formatted']
        if len(periods) > 1 and periods[1]['formatted']:
            formatted_date += f" et {periods[1]['formatted']}"

        return {
            'formatted_date': formatted_date,
            'duration': duration_days,
            'duration_e': duration_days_e,
            'start_date': start_date,
            'end_date': end_date,
            'start_date_e': start_date_e,
            'end_date_e': end_date_e,
            'working_days': working_days,
            'working_days_e': working_days_e
        }

    except ValueError as e:
        print(f"Erreur lors de la conversion des dates: {e}")
        return {
            'formatted_date': f"{date_debut} au {date_fin}",
            'duration': None,
            'duration_e': None,
            'start_date': None,
            'end_date': None,
            'start_date_e': None,
            'end_date_e': None,
            'working_days': [],
            'working_days_e': []
        }
# Exemple d'utilisation
resultat = format_date_range(
    "10/02/24",  # Jeudi
    "15/02/24",  # Lundi
    "06/02/24",  # Mardi
    "09/02/24",  # Vendredi
    have_sunday=True,
    have_saturday=True
)

# Cela exclura samedi (03/02) et dimanche (04/02)
print(resultat['formatted_date'])
print(f"Durée en jours (présentiel): {resultat['duration']}")
print(f"Durée en jours (e-learning): {resultat['duration_e']}")
print("Jours de formation (présentiel):", [d.strftime("%d/%m/%Y") for d in resultat['working_days']])
print("Jours de formation (e-learning):", [d.strftime("%d/%m/%Y") for d in resultat['working_days_e']])