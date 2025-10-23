from django.urls import path
from . import views_almacen as v

app_name = 'almacen'

urlpatterns = [
    path('inventario/', v.inventario_list, name='inventario'),
    path('inventario/<int:pk>/ajustar/', v.ajustar_stock, name='ajustar'),
    path('movimientos/', v.movimientos_list, name='movimientos'),
]
