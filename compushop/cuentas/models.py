from django.db import models
from django.contrib.auth.models import AbstractUser  # No Aparece por defecto.
from django.conf import settings  # No Aparece por defecto.
from django.utils.translation import gettext_lazy as _  # No Aparece por defecto.

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


class ConfiguracionUsuario(models.Model):
    """
    Modelo que almacena las preferencias de visualización del dashboard
    para cada usuario (roles: gerencia, ventas, almacén).
    """
    # OneToOneField relaciona cada configuración a un único usuario.
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = 'configuracion'
    )

    # Métricas seleccionadas por el usuario. JSONField para mayor flexibilidad.
    metricas_activas = models.JSONField(
        default = dict,
        help_text = _("Diccionario con las métricas activas en el dashboard.")
    )

    # Otras preferencias.
    tema = models.CharField(
        max_length=20,
        choices=[
            ('claro', _('Modo claro')),
            ('oscuro', _('Modo oscuro')),
        ],
        default='claro',
    )

    mostrar_tendencias = models.BooleanField(
        default=True,
        help_text=_("Indica si se visualizan los gráficos de tendencia.")
    )

    mostrar_alertas = models.BooleanField(
        default=True,
        help_text=_("Mostrar alertas de stock y rendimiento automáticamente")
    )

    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Configuración de usuario")
        verbose_name_plural = _("Configuraciones de usuarios")

    def __str__(self):
        return f'Configuración de {self.usuario.username}'
