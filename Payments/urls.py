from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetDoneView, PasswordResetCompleteView
from django.urls import path, reverse_lazy
from django.conf import settings

from . import views


app_name = 'Payments'
urlpatterns = [
    path('add-doc/', views.submit_payment_document, name='add-doc'),
    path('history/', views.history, name='history'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
