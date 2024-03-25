from django.urls import path, re_path
from django.views.i18n import set_language

from . import views
from .views import register_magistrat

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('sign-up', views.sign_up, name='sign_up'),
    path('register-magistrat/', register_magistrat, name='register_magistrat'),
    path('create-expense', views.create_expense, name='create_expense'),
    re_path(r'^i18n/setlang/$', set_language, name='set_language'),
]
