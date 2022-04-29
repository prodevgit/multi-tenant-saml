from api.v1 import views
from django.urls import path

urlpatterns = [
    path('auth/login', views.LoginView.as_view(), name='auth-login'),
    path('auth/login-saml', views.LoginSamlView.as_view(), name='auth-login-saml'),
    path('auth/set-token', views.SetSAMLTokenView.as_view(), name='auth-set-token'),
    path('auth/logout', views.LogoutView.as_view(), name="auth-logout"),
    path('tenant/create', views.TenantCreateView.as_view(), name='tenant-create'),
]
