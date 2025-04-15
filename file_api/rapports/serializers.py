from rest_framework import serializers

from file_api.models import Client, Site, InspectionType, Rapport, Etiquette, QRCode


class ClientSerializerSite(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class SiteSerializer(serializers.ModelSerializer):
    client = ClientSerializerSite()

    class Meta:
        model = Site
        fields = ['id', 'name', 'address', 'contact', 'email', 'client']
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def create(self, validated_data):
        client_data = validated_data.pop('client')

        # Vérifie si le client existe déjà
        client, created = Client.objects.get_or_create(id=client_data.get('id'), defaults=client_data)

        # Crée le site avec le client trouvé ou créé
        site = Site.objects.create(client=client, **validated_data)
        return site

    def update(self, instance, validated_data):
        client_data = validated_data.pop('client', None)

        if client_data:
            client = Client.objects.get(id=client_data.get('id'))
            instance.client = client

        instance.name = validated_data.get('name', instance.name)
        instance.address = validated_data.get('address', instance.address)
        instance.contact = validated_data.get('contact', instance.contact)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance



class ClientSerializer(serializers.ModelSerializer):
    sites = SiteSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = '__all__'


class InspectionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionType
        fields = '__all__'

class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = ['id', 'code', 'image', 'url', 'numero']



class EtiquetteSerializer(serializers.ModelSerializer):
    qrcode = QRCodeSerializer(read_only=True)

    class Meta:
        model = Etiquette
        fields = ['id', 'site', 'inspectionType', 'numero', 'qrcode', 'isAssigned']


class RapportSerializer(serializers.ModelSerializer):
    etiquette = serializers.PrimaryKeyRelatedField(queryset=Etiquette.objects.all())
    qrcode = QRCodeSerializer(read_only=True)  # QR Code en lecture seule, dérivé de l'étiquette

    class Meta:
        model = Rapport
        fields = ['id', 'numero_rapport', 'fichier', 'date_inspection', 'etiquette', 'qrcode', 'inspectionType', 'site']
        read_only_fields = ['id', 'qrcode']  # 'qrcode' est en lecture seule

    def create(self, validated_data):
        # Récupérer l'étiquette et son QR Code associé
        etiquette = validated_data.get('etiquette')
        if not etiquette:
            raise serializers.ValidationError({"etiquette": "Une étiquette doit être associée au rapport."})

        qrcode = etiquette.qrcode
        if not qrcode:
            raise serializers.ValidationError({"qrcode": "L'étiquette sélectionnée n'a pas de QR Code associé."})

        validated_data['qrcode'] = qrcode  # Associer le QR Code au rapport
        rapport = Rapport.objects.create(**validated_data)
        return rapport

    def update(self, instance, validated_data):
        # Mettre à jour les champs du rapport
        instance.numero_rapport = validated_data.get('numero_rapport', instance.numero_rapport)
        instance.fichier = validated_data.get('fichier', instance.fichier)
        instance.date_inspection = validated_data.get('date_inspection', instance.date_inspection)
        instance.inspectionType = validated_data.get('inspectionType', instance.inspectionType)
        instance.site = validated_data.get('site', instance.site)

        # Si l'étiquette est modifiée, mettre à jour le QR Code en conséquence
        if 'etiquette' in validated_data:
            etiquette = validated_data.get('etiquette')
            qrcode = etiquette.qrcode
            if not qrcode:
                raise serializers.ValidationError({"qrcode": "L'étiquette sélectionnée n'a pas de QR Code associé."})
            instance.etiquette = etiquette
            instance.qrcode = qrcode

        instance.save()
        return instance

    def validate(self, data):
        # Validation supplémentaire si nécessaire
        if not data.get('etiquette'):
            raise serializers.ValidationError("Une étiquette doit être associée au rapport.")
        return data


class RapportListSerializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)
    inspectionType = InspectionTypeSerializer(read_only=True)

    class Meta:
        model = Rapport
        fields = ['id', 'site', 'inspectionType', 'fichier', 'date_inspection']


class RapportCreateSerializer(serializers.ModelSerializer):
    site = serializers.PrimaryKeyRelatedField(queryset=Site.objects.all())
    inspectionType = serializers.PrimaryKeyRelatedField(queryset=InspectionType.objects.all())

    class Meta:
        model = Rapport
        fields = ['numero_rapport', 'site', 'inspectionType', 'qrcode', 'fichier', 'file', 'file', 'date_inspection']
