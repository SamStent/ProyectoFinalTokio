from django.contrib import admin
from .models import Orden, ItemOrden
from django.utils.safestring import mark_safe
import csv
import datetime
from django.http import HttpResponse
from django.urls import reverse
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
        html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
        # django escapa la salida HTML por defecto. Usamos la función
        # mark_safe para evitar el escape automático.
        return mark_safe(html)
    return ''

pago_orden.short_description = 'Stripe payment'

def exportar_a_csv(modeladmin, request, queryset):
    opciones = modeladmin.model._meta
    disposicion_contenido = (
        f'attachment; filename={opciones.verbose_name}.csv'
    )
    # Creamos una instancia de HttpResponse, especificando text/csv en el
    # content type, para decirle al browser que la respuesta tiene que ser
    # tratada como un archivo CSV.
    respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
    respuesta['Content-Disposition'] = disposicion_contenido
    # Creamos un objeto writer para escribir al objeto respuesta
    escritor = csv.writer(respuesta)
    campos = [
        campo
        for campo in opciones.get_fields()
        if not campo.many_to_many and not campo.one_to_many
    ]
    # Escribir el encabezado en la primer línea.
    escritor.writerow([campo.verbose_name for campo in campos])
    # Iteramos el queryset recibido
    for obj in queryset:
        datos_fila = []
        for campo in campos:
            # Obtenemos el valor de cada campo con getattr
            valor = getattr(obj, campo.name)
            # Si hay un objeto datetime debemos pasarlo a string para el CSV
            if isinstance(valor, datetime.datetime):
                valor = valor.strftime('%d/%m/%Y')
            datos_fila.append(valor)
        escritor.writerow(datos_fila)
    return respuesta

# Customizamos el nombre de la acción en el drop-down del admin
exportar_a_csv.short_description = 'Exportar a CSV'


def detalle_orden(obj):
    url = reverse('ordenes:detalle_orden_admin', args=[obj.id])
    return mark_safe(f'<a href="{url}">Vista</a>')


def pdf_orden(obj):
    url = reverse('ordenes:orden_admin_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')

pdf_orden.short_description = 'Invoice'


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'usuario',
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
        'creado',
        detalle_orden,
        pdf_orden,
        ]
    list_filter = ['pagado', 'creado', 'usuario', 'actualizado']
    search_fields = ['id', 'email', 'usuario__username']
    inlines = [ItemOrdenEnLinea]
    actions = [exportar_a_csv]
