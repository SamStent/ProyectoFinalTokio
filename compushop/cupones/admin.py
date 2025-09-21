from django.contrib import admin
from .models import Cupon

# Register your models here.

@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = [
        'codigo',
        'valido_desde',
        'valido_hasta',
        'descuento',
        'activo'
    ]
    list_filter = ['activo', 'valido_desde', 'valido_hasta']
    search_fields = ['code']
