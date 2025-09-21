from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from tienda.models import Producto
from .carro import Carro
from .forms import FormularioAniadir
from cupones.forms import FormularioAplicarCupon

# Create your views here.


@require_POST
def aniadir_a_carro(request, id_producto):
    carro = Carro(request)
    producto = get_object_or_404(Producto, id=id_producto)
    formulario = FormularioAniadir(request.POST)
    if formulario.is_valid():
        cd = formulario.cleaned_data
        carro.aniadir(
            producto=producto,
            cantidad=cd['cantidad'],
            actualizar_cantidad=cd['actualizar']
        )
    return redirect('carro:detalle_carro')


@require_POST
def eliminar_carro(request, id_producto):
    '''
        Elimina los items del carro.
        Paramétros:
            - id_producto
    '''
    carro = Carro(request)
    producto = get_object_or_404(Producto, id=id_producto)
    carro.eliminar(producto)
    return redirect('carro:detalle_carro')


def detalle_carro(request):
    carro = Carro(request)
    for item in carro:
        item['formulario_actualizar_cantidad'] = FormularioAniadir(
            initial={'cantidad': item['cantidad'], 'actualizar_cantidad':True}
        )
    formulario_aplicar_cupon = FormularioAplicarCupon()
    return render(
        request,
        'carro/detalle.html',
        {
            'carro': carro,
            'formulario_aplicar_cupon': formulario_aplicar_cupon
        }
    )
