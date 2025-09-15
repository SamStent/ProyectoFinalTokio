from django.contrib import admin
from .models import Categoria, Producto

# Register your models here.

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug']
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre',
        'slug',
        'precio',
        'disponible',
        'creado',
        'actualizado'
    ]
    # Campos para filtrar desde el admin
    list_filter = ['disponible', 'creado', 'actualizado']
    # Campos que se pueden editar desde el admin, puede ser cualquiera de
    # los que se incluyen en list_display.
    list_editable = ['precio', 'disponible']
    # Campos cuyo valor se configuran usando el valor de otros campos.
    prepopulated_fields = {'slug': ('nombre',)}
