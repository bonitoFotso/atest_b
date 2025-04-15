from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import User, Inspecteur, Formateur
from .serializers import UserSerializer, InspecteurSerializer, FormateurSerializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # La déconnexion nécessite d'être authentifié

    def post(self, request):
        try:
            # Récupérer le token de rafraîchissement depuis le corps de la requête
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"detail": "No refresh token provided."}, status=status.HTTP_400_BAD_REQUEST)

            # Blacklister le token de rafraîchissement
            token = RefreshToken(refresh_token)
            token.blacklist()  # Ajout du token à la blacklist

            return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Protection par authentification

# Vue pour renvoyer les informations de l'utilisateur connecté
class UserDetailViews(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]  # Assure que l'utilisateur est authentifié
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        user = request.user  # Récupère l'utilisateur connecté grâce au token
        serializer = self.get_serializer(user)  # Sérialise les données de l'utilisateur
        return Response(serializer.data)  # Retourne les données sérialisées


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Protection par authentification
    lookup_field = 'id'

class InspecteurListCreateView(generics.ListCreateAPIView):
    queryset = Inspecteur.objects.all()
    serializer_class = InspecteurSerializer
    permission_classes = [IsAuthenticated]

class InspecteurDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Inspecteur.objects.all()
    serializer_class = InspecteurSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

class FormateurListCreateView(generics.ListCreateAPIView):
    queryset = Formateur.objects.all()
    serializer_class = FormateurSerializer
    permission_classes = [IsAuthenticated]

class FormateurDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Formateur.objects.all()
    serializer_class = FormateurSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


