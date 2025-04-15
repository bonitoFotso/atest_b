from django.core.management.base import BaseCommand

from apps.clients.models import Client


class Command(BaseCommand):
    help = 'Seed clients into the database'

    def handle(self, *args, **kwargs):
        clients = [
            "PAK", "BROLI", "RADIO BALAFON", "CIMAF", "PERENCO", "DANGOTE", "CHOCOCAM", "NESTLE",
            "AGL", "SCDP", "CNPS", "KPDC", "DPDC", "TELCAR", "ALUCAM", "CADYST", "SCB",
            "AFRILAND FIRST BANK", "CCA", "BANQUE ATLANTIQUE", "BGFI", "FEICOM", "HOTEL LA FALAISE",
            "HOTEL IBIS", "CARREFOUR", "SANTA LUCIA", "ORANGE", "MTN", "SIC CACAO", "PAD",
            "SIKA", "CIMENCAM", "TRADEX", "NEPTURNE", "OLA ENERGY", "PROMETAL", "BIOPHARMA",
            "OK FOOD", "NEW FOOD", "SOLEVO", "CAMI", "ORCA", "SOTICAM", "BOCOM", "BEAC",
            "GUINESS", "SODECOTON", "UBIPHARM", "LABOREX", "ICRAFON", "MIA", "SMALTO",
            "SOFAVIN", "TOTAL", "CONGELCAM", "ALPICAM", "RTC", "HEVECAM", "MIRA", "COTCO",
            "GULFIN", "BLESSING", "PHALUCAM", "SOURCE DU PAYS", "ACERO METAL", "UCB",
            "OK PLAST", "OLAM CAM", "METAFRIQUE", "SGMC", "PHP", "AZUR", "SONATREL",
            "CENTRE PASTEUR", "SOCAPALM", "MITCH CHIMIE", "TRACTAFRIC", "BIA CAMEROUN",
            "AIR LIQUIDE", "CBC BANK", "COGENI", "QUIFEROU", "DOVV", "SPARK", "MAHIMA",
            "NOVIA", "PETROLEX", "PLASTICAM", "RAZEL", "SAAGRY", "SAFACAM", "PRIMO",
            "SEPBC", "SNI", "SONARA", "SOSUCAM", "TAC", "ZATI CONSTRUCTION", "ENEO"
        ]

        for client_name in clients:
            client, created = Client.objects.get_or_create(name=client_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Client {client_name} créé avec succès."))
