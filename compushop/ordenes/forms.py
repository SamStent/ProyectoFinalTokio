from django import forms
from .models import Orden


class FormularioCrearOrden(forms.ModelForm):
    class Meta:
        model = Orden
        fields = [
            'nombre',
            'primer_apellido',
            'segundo_apellido',
            'email',
            'direccion',
            'codigo_postal',
            'poblacion'
        ]
