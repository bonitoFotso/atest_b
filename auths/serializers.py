from rest_framework import serializers
from .models import User, Inspecteur, Formateur
from django.contrib.auth.models import Group, Permission
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Ajouter des informations personnalisées au token
        token['full_name'] = user.full_name
        token['user_type'] = user.user_type

        return token


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    # Sérialisation des groupes d'utilisateurs (Admin, Editor, Viewer, etc.)
    groups = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Group.objects.all()
    )
    staff_type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'is_active', 'is_staff', 'staff_type', 'groups', 'created_at',
                  'updated_at', 'email_verified']
        read_only_fields = ['id', 'staff_type', 'created_at', 'updated_at', 'email_verified']

    def get_staff_type(self, obj):
        return obj.staff_type()

    def create(self, validated_data):
        # Créer un utilisateur avec les données validées
        groups_data = validated_data.pop('groups', [])
        user = User.objects.create_user(**validated_data)
        user.groups.set(groups_data)
        return user

    def update(self, instance, validated_data):
        # Mettre à jour un utilisateur avec les données validées
        groups_data = validated_data.pop('groups', [])
        instance = super().update(instance, validated_data)
        instance.groups.set(groups_data)
        return instance


class DetailedUserSerializer(serializers.ModelSerializer):
    # Sérialisation des groupes avec leurs détails
    groups = GroupSerializer(many=True)

    # Sérialisation des permissions directement liées à l'utilisateur
    user_permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'is_active', 'is_staff', 'groups', 'user_permissions',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']




# class UserSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = User
#        fields = ('id', 'email', 'full_name', 'is_active', 'is_staff', 'email_verified', 'created_at', 'updated_at')
#        read_only_fields = ('id', 'is_staff', 'is_active', 'created_at', 'updated_at')


class InspecteurSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Inspecteur
        fields = ('id', 'user', 'specialisation', 'zone_inspection')


class FormateurSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Formateur
        fields = ('id', 'user', 'expertise', 'years_experience')


