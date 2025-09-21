from decimal import ROUND_HALF_UP, Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from cupones.models import Cupon
from django.db import models
from django.conf import settings

# Create your models here.


class Orden(models.Model):
    nombre = models.CharField(max_length=50)
    primer_apellido = models.CharField(max_length=50)
    segundo_apellido = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    direccion = models.CharField(max_length=250)
    codigo_postal = models.CharField(max_length=20)
    poblacion = models.CharField(max_length=100)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    pagado = models.BooleanField(default=False)
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
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        ordering = ['-creado']
        indexes = [
            models.Index(fields=['-creado']),
        ]

    def __str__(self):
        return f'Orden {self.id}'

    def precio_total(self):
        total = self.total_antes_descuento() - self.obtener_descuento()
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def obtener_url_stripe(self):
        if not self.stripe_id:
            # No se asocia un pago
            return ''
        if '_test_' in settings.STRIPE_SECRET_KEY:
            # Path de Stripe para los test de pagos
            path = '/test/'
        else:
            # Path de Stripe para pagos reales
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
        max_digits=10,
        decimal_places=2
    )
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def obtener_precio(self):
        return self.precio * self.cantidad
