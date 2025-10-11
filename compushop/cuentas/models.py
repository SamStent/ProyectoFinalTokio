from django.db import models
from django.contrib.auth.models import AbstractUser  # No Aparece por defecto.

# Create your models here.

class Usuario(AbstractUser):
    TIPOS_CUENTA = (
        ('cliente', 'Cliente'),
        ('personal', 'Personal'),
    )
    tipo_cuenta = models.CharField(
        max_length=20,
        choices=TIPOS_CUENTA,
        default='cliente'
    )
    ROLES_PERSONAL = (
        ('almacen', 'Almacén'),
        ('ventas', 'Ventas'),
        ('gerencia', 'Gerencia'),
    )
    rol_personal = models.CharField(
        max_length=20,
        choices=ROLES_PERSONAL,
        blank=True,
        null=True,
        help_text="Solo para usuarios del tipo 'personal'."
    )

    def es_cliente(self):
        return self.tipo_cuenta == 'cliente'

    def es_personal(self):
        return self.tipo_cuenta == 'personal'

    def __str__(self):
        return self.username
