from django.urls import path
from django.contrib.auth import views as auth_views
from . import views, views_dashboard
from .views import CustomLoginView

app_name = 'cuentas'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path(
        'login/',
        CustomLoginView.as_view(template_name='cuentas/login.html'),
        name='login'
    ),
    path('logout/', auth_views.LogoutView.as_view(next_page='cuentas:login'), name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('personal/', views.panel_personal, name='panel_personal'),
    path('almacen/', views.panel_almacen, name='panel_almacen'),
    path('ventas/', views.panel_ventas, name='panel_ventas'),
    path('gerencia/', views.panel_gerencia, name='panel_gerencia'),
    path('gerencia/dashboard-metricas', views_dashboard.dashboard_view, name='dashboard_metricas'),
    path('gerencia/config_panel', views_dashboard.config_panel, name='config_panel'),
    path('configuracion/', views_dashboard.config_panel, name='config_panel'),
]
