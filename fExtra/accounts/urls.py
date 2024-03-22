from django.urls import path
from . import views

urlpatterns = [
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('connexion/magistrat/', views.connexion_magistrat, name='connexion_magistrat'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('home/', views.home, name='home'),
]
