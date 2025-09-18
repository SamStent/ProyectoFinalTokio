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

    class Meta:
        ordering = ['-creado']
        indexes = [
            models.Index(fields=['-creado']),
        ]

    def __str__(self):
        return f'Orden {self.id}'

    def precio_total(self):
        return sum(item.obtener_precio() for item in self.items.all())

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
