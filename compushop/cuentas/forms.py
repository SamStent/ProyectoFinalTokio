from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import Usuario, ConfiguracionUsuario


class RegistroClienteForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': _('Nombre de usuario'),
            'email': _('Correo electrónico'),
            'password1': _('Contraseña'),
            'password2': _('Confirmar contraseña'),
        }
        help_text = {
            'username': _('Introduce un nombre único para tu cuenta.'),
            'email': _('Lo utilizaremos para notificaciones y confirmaciones.'),
            'password1': _('Introduce una contraseña válida.'),
            'password2': _('Repite tu contraseña.'),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo_cuenta = 'cliente'
        if commit:
            user.save()
        return user



# Opciones disponibles de métricas
METRICAS_CHOICES = [
    ("grafico_stock", _("Gráfico de stock total")),
    ("grafico_precios", _("Gráfico de precios medios")),
    ("rendimiento_proveedor", _("Rendimiento por proveedor")),
    ("rotacion_productos", _("Rotación de productos")),
    ("alertas_stock", _("Alertas de stock bajo")),
]

class ConfiguracionUsuarioForm(forms.ModelForm):
    """
    Formulario de configuración del dashboard personal.
    Muestra las métricas según el rol del usuario (gerencia, ventas o almacén).
    """

    # Listas de métricas por rol
    METRICAS_POR_ROL = {
        "almacen": [
            ("existencias", _("Existencias por proveedor")),
            ("rotacion", _("Rotación de productos")),
            ("distribucion_stock", _("Distribución del stock")),
            ("alertas_stock", _("Alertas de bajo stock")),
        ],
        "ventas": [
            ("rendimiento", _("Rendimiento por proveedor")),
            ("precio_medio", _("Precio medio por proveedor")),
            ("distribucion_stock", _("Distribución del stock")),
            ("alertas_stock", _("Alertas de bajo stock")),
        ],
        "gerencia": [
            ("valor_stock", _("Valor de stock por proveedor")),
            ("rendimiento", _("Rendimiento por proveedor")),
            ("precio_medio", _("Precio medio por proveedor")),
            ("rotacion", _("Rotación de productos")),
            ("distribucion_stock", _("Distribución del stock")),
            ("alertas_stock", _("Alertas de bajo stock")),
        ],
    }

    metricas_activas = forms.MultipleChoiceField(
        choices=[],  # se setean dinámicamente en __init__
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        required=False,
        label=_("Métricas activas"),
        help_text=_("Selecciona las métricas que deseas mostrar en tu panel."),
    )

    class Meta:
        model = ConfiguracionUsuario
        fields = ["metricas_activas", "tema", "mostrar_tendencias", "mostrar_alertas"]
        labels = {
            "tema": _("Tema visual"),
            "mostrar_tendencias": _("Mostrar gráficos de tendencia"),
            "mostrar_alertas": _("Mostrar alertas automáticas"),
        }
        widgets = {
            "tema": forms.Select(attrs={"class": "form-select"}),
            "mostrar_tendencias": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "mostrar_alertas": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop("usuario", None)
        super().__init__(*args, **kwargs)

        # Determinar el rol actual del usuario
        rol = getattr(usuario, "rol_personal", "personal").lower() if usuario else "personal"

        # Asignar métricas dinámicamente
        self.fields["metricas_activas"].choices = self.METRICAS_POR_ROL.get(rol, [])

        # Marcar las métricas que ya estaban activas
        metricas_guardadas = self.instance.metricas_activas or {}
        seleccionadas = [clave for clave, valor in metricas_guardadas.items() if valor]
        self.initial["metricas_activas"] = seleccionadas

    def clean_metricas_activas(self):
        seleccionadas = self.cleaned_data.get("metricas_activas", [])
        # convertir lista -> dict con booleanos (True/False)
        todas = dict(self.fields["metricas_activas"].choices)
        return {clave: (clave in seleccionadas) for clave in todas.keys()}
