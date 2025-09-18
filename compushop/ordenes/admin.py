from django.contrib import admin
from .models import Orden, ItemOrden
from django.utils.safestring import mark_safe
'''
    Se desaconseja usar mark_safe en la entrada del usuario para evitar ataques
    de secuencias de comandos entre sitios (XSS). Estos ataques permiten a los
    atacantes inyectar scripts del lado del cliente en el contenido web que
    ven otros usuarios.
'''

# Register your models here.

class ItemOrdenEnLinea(admin.TabularInline):
    model = ItemOrden
    raw_id_fields = ['producto']


def pago_orden(obj):
    url = obj.obtener_url_stripe()
    if obj.stripe_id:
        html = f'<a href="url" target="_blank">{obj.stripe_id}</a>'
        # django escapa la salida HTML por defecto. Usamos la función
        # mark_safe para evitar el escape automático.
        return mark_safe(html)
    return ''
pago_orden.short_description = 'Stripe payment'

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
        pago_orden,
        'actualizado',
        'creado'
        ]
    list_filter = ['pagado', 'creado', 'actualizado']
    inlines = [ItemOrdenEnLinea]
