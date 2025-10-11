from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import Usuario


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
