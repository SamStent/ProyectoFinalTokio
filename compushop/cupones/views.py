from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import FormularioAplicarCupon
from .models import Cupon

# Create your views here.

@require_POST # Restringe la vista a POST requests.
def aplicar_cupon(request):
    '''
        Valida el cupon y lo guarda en la sesión de usuario.
    '''
    ahora = timezone.now()
    # Instanciamos FormularioAplicarCupon usando la data del post y
    # chequeamos que sea válido.
    formulario = FormularioAplicarCupon(request.POST)
    if formulario.is_valid():
        # Obtenemos el código del diccionario 'cleaned_data' del formulario.
        codigo = formulario.cleaned_data['codigo']
        try:
            cupon = Cupon.objects.get(
                codigo__iexact=codigo,
                valido_desde__lte=ahora,
                valido_hasta__gte=ahora,
                activo=True
            )
            # Guardamos el id del cupon en la session de usuario.
            request.session['id_cupon'] = cupon.id
        except Cupon.DoesNotExist:
            request.session['id_cupon'] = None
    return redirect('carro:detalle_carro')
