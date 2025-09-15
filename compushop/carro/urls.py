from django.urls import path
from . import views

app_name = 'carro'
urlpatterns = [
    path('', views.detalle_carro, name='detalle_carro'),
    path('add/<int:id_producto>/', views.aniadir_a_carro, name='aniadir_a_carro'),
    path(
        'remove/<int:id_producto>/',
        views.eliminar_carro,
        name='eliminar_carro'
    ),
]
