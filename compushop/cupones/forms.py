from django import forms

class FormularioAplicarCupon(forms.Form):
    codigo = forms.CharField()
