from django.urls import path
from .views import (
    UserListCreateView, UserDetailView,
    InspecteurListCreateView, InspecteurDetailView,
    FormateurListCreateView, FormateurDetailView,
 UserDetailViews, LogoutView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # Routes pour User
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:id>/', UserDetailView.as_view(), name='user-detail'),
    path('users/me/', UserDetailViews.as_view(), name='user-detail'),

    # Routes pour Inspecteur
    path('inspecteurs/', InspecteurListCreateView.as_view(), name='inspecteur-list-create'),
    path('inspecteurs/<int:id>/', InspecteurDetailView.as_view(), name='inspecteur-detail'),

    # Routes pour Formateur
    path('formateurs/', FormateurListCreateView.as_view(), name='formateur-list-create'),
    path('formateurs/<int:id>/', FormateurDetailView.as_view(), name='formateur-detail'),

    # Routes pour Participant

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', LogoutView.as_view(), name='logout'),  # Ajout de l'URL de déconnexion

]

