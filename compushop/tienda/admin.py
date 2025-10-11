from django.contrib import admin
from .models import Categoria, Producto, Proveedor

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
        'stock',
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


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = [
        'nombre_empresa',
        'cif',
        'telefono',
        'activo',
        'total_productos',
        'productos_disponibles',
        'valor_stock_total'
    ]
    search_fields = [
        'nombre_empresa',
        'cif', 'email'
    ]
    list_filter = [
        'activo',
        'fecha_alta'
    ]

    @admin.display(description='Total productos')
    def total_productos(self, obj):
        return obj.total_productos

    @admin.display(description='Productos disponibles')
    def productos_disponibles(self, obj):
        return obj.productos_disponibles


    @admin.display(description='Valor total stock (€)')
    def valor_stock_total(self, obj):
        return f'{obj.valor_stock_total:.2} €'
