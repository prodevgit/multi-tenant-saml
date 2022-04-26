from api.v1 import views
from django.urls import path

urlpatterns = [
    path('auth/login', views.LoginSamlView.as_view(), name='auth-login'),
    path('auth/set-token', views.SetSAMLTokenView.as_view(), name='auth-set-token'),
    path('auth/logout', views.LogoutView.as_view(), name="auth-logout"),
]
