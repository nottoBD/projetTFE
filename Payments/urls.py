from django.conf.urls.static import static
from django.urls import path, reverse_lazy
from django.conf import settings

from . import views
from .views import PaymentHistoryView

app_name = 'Payments'
urlpatterns = [
    path('add-doc/', views.submit_payment_document, name='add-doc'),
    path('history/', PaymentHistoryView.as_view(), name='history'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
