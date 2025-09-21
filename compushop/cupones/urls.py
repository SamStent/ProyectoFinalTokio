from django.urls import path
from . import views

app_name ='cupones'
urlpatterns = [
    path('aplicar/', views.aplicar_cupon, name='aplicar'),
]
