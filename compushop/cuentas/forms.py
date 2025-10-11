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
            'password2': _('Repite tu contraseña'),
        }



# Opciones disponibles de métricas
METRICAS_CHOICES = [
    ("grafico_stock", _("Gráfico de stock total")),
    ("grafico_precios", _("Gráfico de precios medios")),
    ("rendimiento_proveedor", _("Rendimiento por proveedor")),
    ("rotacion_productos", _("Rotación de productos")),
    ("alertas_stock", _("Alertas de stock bajo")),
]

class ConfiguracionUsuarioForm(forms.ModelForm):
    metricas_activas = forms.MultipleChoiceField(
        choices=METRICAS_CHOICES,
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
        super().__init__(*args, **kwargs)
        # Si hay un JSON ya guardado, marcar los checkboxes correspondientes
        metricas = self.instance.metricas_activas or {}
        seleccionadas = [k for k, v in metricas.items() if v]
        self.initial["metricas_activas"] = seleccionadas

    def clean_metricas_activas(self):
        seleccionadas = self.cleaned_data.get("metricas_activas", [])
        # Convertimos la lista en dict con valores booleanos
        return {clave: (clave in seleccionadas) for clave, _ in METRICAS_CHOICES}
