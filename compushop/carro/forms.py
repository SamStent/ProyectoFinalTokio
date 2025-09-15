from django import forms

CANTIDAD_PRODUCTO_OPCIONES = [(i, str(i)) for i in range(1, 21)]
class FormularioAniadir(forms.Form):
    # Permite al usuario seleccionar la cantidad entre 1 y 20
    cantidad = forms.TypedChoiceField(
        choices=CANTIDAD_PRODUCTO_OPCIONES,
        coerce=int
    )
    # Indica si la cantidad tiene que ser actualizada(True) o sumada(False)
    actualizar = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )
