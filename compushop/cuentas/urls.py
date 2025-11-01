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
    path('logout/', views.logout_usuario, name='logout'),
    path('panel/cliente/', views.panel_cliente, name='panel_cliente'),
    path('personal/', views.panel_personal, name='panel_personal'),
    path('almacen/', views.panel_almacen, name='panel_almacen'),
    path('ventas/', views.panel_ventas, name='panel_ventas'),
    path('gerencia/', views.panel_gerencia, name='panel_gerencia'),
    path('<str:rol>/dashboard/', views_dashboard.dashboard_view, name='dashboard_view'),
    path('gerencia/config_panel', views_dashboard.config_panel, name='config_panel'),
    path('panel/ventas/inventario', views.inventario_acceso_ventas, name='inventario_ventas'),
    path('configuracion/', views_dashboard.config_panel, name='config_panel'),
    path('configuracion/almacen/', views_dashboard.config_almacen, name='config_almacen')
]
