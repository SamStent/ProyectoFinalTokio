from django.contrib import admin
from .models import Orden, ItemOrden

# Register your models here.

class ItemOrdenEnLinea(admin.TabularInline):
    model = ItemOrden
    raw_id_fields = ['producto']


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'nombre',
        'primer_apellido',
        'segundo_apellido',
        'email',
        'direccion',
        'codigo_postal',
        'poblacion',
        'pagado',
        'actualizado',
        'creado'
        ]
    list_filter = ['pagado', 'creado', 'actualizado']
    inlines = [ItemOrdenEnLinea]
