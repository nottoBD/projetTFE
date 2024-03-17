from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.requete_inscription, name='s\'inscrire'),
    # TODO: chemins connexion,déconnexion
]
