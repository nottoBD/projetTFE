from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.i18n import set_language
from django.conf import settings
from fExtra import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('Payments/', include('Payments.urls', namespace='Payments')),
    re_path(r'^i18n/setlang/$', set_language, name='set_language'),
    path('', views.home, name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
