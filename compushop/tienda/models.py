from django.db import models
from django.urls import reverse

# Create your models here.


class Categoria(models.Model):
    """
    Modelo que representa una categoría de productos.
    Incluye un nombre y un slug único para URL.
    """

    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    class Meta:
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
        ]
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

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
        related_name='productos',
        on_delete=models.CASCADE
    )
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    imagen = models.ImageField(
        upload_to='productos/%Y/%m/%d',
        blank=True
    )
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['nombre']),
            models.Index(fields=['-creado']),
        ]

    def get_absolute_url(self):
        return reverse(
            'tienda:detalle_producto', args=[self.id, self.slug]
        )

    def __str__(self):
        return self.nombre
