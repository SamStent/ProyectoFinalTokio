from django import forms

class AjusteStockForm(forms.Form):
    cantidad = forms.IntegerField(min_value=1, help_text="Usa signo + para entrada, - para salida en el campo de tipo.")
    tipo = forms.ChoiceField(choices=[('entrada','Entrada'),('salida','Salida'),('ajuste','Ajuste')])
    motivo = forms.CharField(required=False)
    referencia = forms.CharField(required=False)
