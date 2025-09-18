from django.urls import path
from . import views

app_name = 'ordenes'
urlpatterns = [
    path('crear', views.crear_orden, name='crear_orden'),
    path('creado', views.orden_creada, name='orden_creada'),
    path(
        'admin/orden/<int:id_orden>/',
        views.detalle_orden_admin,
        name='detalle_orden_admin'
    )
]
