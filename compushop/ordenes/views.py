from django.shortcuts import redirect, render
from carro.carro import Carro
from .forms import FormularioCrearOrden
from .models import ItemOrden
from .tasks import task_orden_creada

# Create your views here.


def crear_orden(request):
    carro = Carro(request)
    if request.method == 'POST':
        formulario = FormularioCrearOrden(request.POST)
        if formulario.is_valid():
            orden = formulario.save()
            for item in carro:
                ItemOrden.objects.create(
                    orden = orden,
                    producto = item['producto'],
                    precio = item['precio'],
                    cantidad = int(item['cantidad'])
                )
            # limpiar el carro
            carro.limpiar()
            # Iniciar asynchronous task
            task_orden_creada.delay(orden.id)
            # Establece la orden en la sesión
            request.session['id_orden'] = orden.id
            # Redirige para pagar
            return redirect('pagos:proceso')

    else:
        formulario = FormularioCrearOrden()
    return render(
        request,
        'ordenes/orden/crear.html',
        {'carro': carro, 'formulario': formulario}
    )


def orden_creada(request):
    return render(request, 'ordenes/creado.html')
