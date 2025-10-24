from decimal import ROUND_HALF_UP, Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from cupones.models import Cupon
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Orden(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='ordenes',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    nombre = models.CharField(_("Nombre"), max_length=50)
    primer_apellido = models.CharField(_("Primer apellido"), max_length=50)
    segundo_apellido = models.CharField(
        _("Segundo apellido"),
        max_length=50,
        blank=True,
        null=True
    )
    email = models.EmailField(_("E-mail"))
    direccion = models.CharField(_("Dirección"), max_length=250)
    codigo_postal = models.CharField(_("Código postal"), max_length=20)
    poblacion = models.CharField(_("Población"), max_length=100)
    creado = models.DateTimeField(_("Creado"), auto_now_add=True)
    actualizado = models.DateTimeField(_("Actualizado"), auto_now=True)
    pagado = models.BooleanField(_("Pagado"), default=False)
    stripe_id = models.CharField(max_length=250,blank=True)

    # Campos para los cupones.
    cupon = models.ForeignKey(
        Cupon,
        related_name='ordenes',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    descuento = models.IntegerField(
        _("Descuento (%)"),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    # Clase Meta, metadatos o atributos de configuración de la clase que
    # definen el comportamiento del modelo a nivel de como django los manipula
    # muestra o guarda.
    class Meta:
        ordering = ['-creado']
        indexes = [
            models.Index(fields=['-creado']),
        ]
        verbose_name = _("Orden")
        verbose_name_plural = _("Órdenes")

    def __str__(self):
        return f'Orden {self.id}'

    def precio_total(self):
        total = self.total_antes_descuento() - self.obtener_descuento()
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def obtener_url_stripe(self):
        if not self.stripe_id:
            # No se asocia un pago.
            return ''
        if '_test_' in settings.STRIPE_SECRET_KEY:
            # Path de Stripe para los test de pagos.
            path = '/test/'
        else:
            # Path de Stripe para pagos reales.
            path = '/'
        return f'https://dashboard.stripe.com{path}payments/{self.stripe_id}'

    def total_antes_descuento(self):
        return sum(item.obtener_precio() for item in self.items.all())

    def obtener_descuento(self):
        total = self.total_antes_descuento()
        if self.descuento:
            descuento = total * (self.descuento / Decimal(100))
            return descuento.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return Decimal('0.00')

    @property
    def estado_display(self):
        return _("Pagada") if self.pagado else _("Pendiente")



class ItemOrden(models.Model):
    orden = models.ForeignKey(
        Orden,
        related_name='items',
        on_delete=models.CASCADE
    )
    producto = models.ForeignKey(
        'tienda.Producto',
        related_name='items_orden',
        on_delete=models.CASCADE
    )
    precio = models.DecimalField(
        _("Precio unitario"),
        max_digits=10,
        decimal_places=2
    )
    cantidad = models.PositiveIntegerField(_("Cantidad"), default=1)

    class Meta:
        verbose_name = _("Item de orden")
        verbose_name_plural = ("Items de orden")

    def __str__(self):
        return str(self.id)

    def obtener_precio(self):
        return self.precio * self.cantidad


# -------------------------------
# Metadatos más comunes en class Meta de un modelo Django:
#
# verbose_name        → Nombre en singular legible (ej: "Orden")
# verbose_name_plural → Nombre en plural legible (ej: "Órdenes")
# ordering            → Orden por defecto de los registros (ej: ['-creado'])
# indexes             → Lista de índices de base de datos para optimizar consultas
# db_table            → Nombre personalizado de la tabla en la base de datos
# unique_together     → Restricción de unicidad en varias columnas (obsoleto, usar constraints)
# constraints         → Restricciones avanzadas en BD (CheckConstraint, UniqueConstraint, etc.)
# permissions         → Permisos adicionales específicos de este modelo
# default_related_name→ Nombre por defecto para las relaciones inversas (related_name)
# get_latest_by       → Campo por el que se obtiene el registro más reciente
#
# Nota: Estos metadatos NO afectan los datos del modelo,
# sino cómo Django lo maneja internamente, en el admin o en la BD.
# Para más detalles sobre los metadatos disponibles (ordering, verbose_name, constraints, etc.),
# véase: https://docs.djangoproject.com/en/5.2/ref/models/options/
# -------------------------------
