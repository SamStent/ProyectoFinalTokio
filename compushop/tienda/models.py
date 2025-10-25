from django.db import models
from django.conf import settings
from django.db.models import Sum, F, FloatField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Categoria(models.Model):
    """
    Modelo que representa una categoría de productos.
    Incluye un nombre y un slug único para URL.
    """

    nombre = models.CharField(_("Nombre"), max_length=200)
    slug = models.SlugField(_("Slug"), max_length=200, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        # Ver models.py en app ordenes para info sobre class Meta en django.
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
        ]
        verbose_name = _("Categoría")
        verbose_name_plural = _("Categorías")

    def get_absolute_url(self):
        return reverse(
            'tienda:listado_productos_por_categoria', args=[self.slug]
        )

    def __str__(self):
        return self.nombre



class Producto(models.Model):
    """
    Modelo que representa un producto dentro del catálogo.

    Campos:
        - categoria: Clave foránea al modelo Categoria. Relación muchos a uno.
        - nombre: Nombre del producto.
        - slug: Identificador corto para URLs amigables.
        - imagen: Imagen asociada al producto (opcional).
        - descripcion: Texto descriptivo del producto (opcional).
        - precio: Precio en formato decimal (hasta 10 dígitos, 2 decimales).
        - disponible: Booleano. Indica si el producto está activo o no.
        - creado: Fecha de creación automática del registro.
        - actualizado: Fecha de última modificación automática.

    Meta:
        - ordering: Ordena los productos por nombre de forma ascendente.
        - indexes: Mejora el rendimiento de búsquedas por id/slug, nombre
        y fecha de creación.
    """

    categoria = models.ForeignKey(
        Categoria,
        verbose_name = _("Categoría"),
        related_name='productos',
        on_delete=models.CASCADE
    )
    nombre = models.CharField(_("Nombre"), max_length=200)
    slug = models.SlugField(_("Slug"), max_length=200)
    imagen = models.ImageField(
        upload_to='productos/%Y/%m/%d',
        blank=True
    )
    descripcion = models.TextField(_("Descripción"), blank=True)
    precio = models.DecimalField(_("Precio"), max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(_("Stock disponible"), default=0)
    stock_minimo = models.PositiveIntegerField(_("Stock Mínimo"), default=10)
    disponible = models.BooleanField(_("Disponible"), default=True)
    creado = models.DateTimeField(_("Creado"), auto_now_add=True)
    actualizado = models.DateTimeField(_("Actualizado"), auto_now=True)
    proveedor = models.ForeignKey(
        'Proveedor',
        on_delete=models.CASCADE,
        related_name='productos', # para buscar productos de un proveedor.
        verbose_name=_("Proveedor"),
    )

    class Meta:
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['nombre']),
            models.Index(fields=['-creado']),
        ]
        verbose_name = _("Producto")
        verbose_name_plural = _("Productos")

    def get_absolute_url(self):
        return reverse(
            'tienda:detalle_producto', args=[self.id, self.slug]
        )

    def necesita_reposicion(self):
        return self.stock <= self.stock_minimo

    def ajustar_stock(self, delta, tipo='ajuste', usuario=None, motivo='', referencia=''):
        self.stock = models.F('stock') + delta
        self.save(update_fields=['stock'])
        self.refresh_from_db(fields=['stock'])
        from .models import StockMovimiento
        StockMovimiento.objects.create(
            producto=self, tipo=tipo, cantidad=delta, motivo=motivo, usuario=usuario, referencia=referencia
        )
        return self.stock

    def __str__(self):
        return self.nombre



class Proveedor(models.Model):
    """
        Modelo que representa un proveedor dentro de la base de datos.
    """

    nombre_empresa = models.CharField(_("Nombre_empresa"), max_length=200)
    cif = models.CharField(_("CIF"), max_length=20, unique=True)
    telefono = models.CharField(_("Telefono"), max_length=20)
    email = models.EmailField(_("Email"), unique=True, blank=True, null=True)
    direccion = models.TextField(_("Dirección"), blank=True)
    descuento = models.FloatField(_("Descuento (%)"), default=0.00)
    iva = models.FloatField(_("IVA (%)"), default=21.00)
    sitio_web = models.URLField(_("Sitio web"), blank=True, null=True)
    fecha_alta = models.DateField(_("Fecha de alta"), auto_now_add=True)
    activo = models.BooleanField(_("Activo"), default=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    @property
    def total_productos(self):
        '''Devuelve el número total de productos asociados a un proveedor.'''
        return self.productos.count()

    @property
    def productos_en_stock(self):
        ''' Calcula los productos en stock asociados a un proveedor.'''
        return self.productos.filter(stock__gt=0).count()

    @property
    def valor_stock_total(self):
        '''
        Calcula el valor del stock de los productos asociados
        un proveedor.
        '''
        resultado = self.productos.aggregate(
            total=Sum(F("precio") * F("stock"), output_field=FloatField())
        )
        return round(resultado['total'] or 0, 2)

    @property
    def productos_disponibles(self):
        '''Devuelve cuántos productos tienen stock disponible.'''
        return self.productos.filter(stock__gt=0).count()

    def __str__(self):
        return self.nombre_empresa


class StockMovimiento(models.Model):
    TIPO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    ]
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPO)
    cantidad = models.IntegerField()
    motivo = models.CharField(max_length=255, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    referencia = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-creado_en']
