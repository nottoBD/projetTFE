from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetDoneView, PasswordResetCompleteView
from django.urls import path, reverse_lazy

from . import views
from .views import register_magistrate, ResetPasswordView, PasswordResetConfirmationView
from django.conf import settings

app_name = 'accounts'
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('accounts:login')), name='logout'),
    path('register/', views.register, name='register'),
    path('register-magistrate/', register_magistrate, name='register_magistrate'),
    path('update/<int:pk>/', views.UserUpdateView.as_view(), name='user_update'),
    path('list/', views.UserListView.as_view(), name='user_list'),
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmationView.as_view(), name='password_reset_confirmation'),
    path('password-reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


