from django.conf.urls.static import static
from django.urls import path
from django.conf import settings

from . import views
from .views import PaymentHistoryView, UserFolderListView, FolderPaymentHistoryView, \
    submit_payment_document_magistrate, PaymentDeleteView

app_name = 'Payments'
urlpatterns = [
    path('add-doc/', views.submit_payment_document, name='add-doc'),
    path('history/', PaymentHistoryView.as_view(), name='history'),
    path('create_folder/', views.create_folder, name='create_folder'),
    path('list_folder/', UserFolderListView.as_view(), name='list_folder'),
    path('folder/<int:folder_id>/history/', FolderPaymentHistoryView.as_view(),name='folder_payment_history'),
    path('Payments/<int:folder_id>/add-doc-magistrate/', submit_payment_document_magistrate, name='add-doc-magistrate'),
    path('payment/<int:pk>/delete/', PaymentDeleteView.as_view(), name='delete_payment'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
