from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy

from . import views
from .views import register_magistrat
from django.conf import settings

app_name = 'accounts'
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('accounts:login')), name='logout'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('register-magistrat/', register_magistrat, name='register_magistrat'),
    path('update/<int:pk>/', views.UserUpdateView.as_view(), name='user_update'),
    path('list/', views.UserListView.as_view(), name='user_list'),
]

#NOTE: Remove from production !!!
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

