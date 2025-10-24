from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from carro.carro import Carro
from .forms import FormularioCrearOrden
from .models import Orden, ItemOrden
from .tasks import task_orden_creada
import weasyprint
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import render_to_string

# Create your views here.


def crear_orden(request):
    carro = Carro(request)
    if request.method == 'POST':
        formulario = FormularioCrearOrden(request.POST)
        if formulario.is_valid():
            orden = formulario.save(commit=False)
            # Asociar el usuario si está autenticado.
            if request.user.is_authenticated:
                orden.usuario = request.user
            # Asegurar consistencia del email si está autenticado.
            if request.user.is_authenticated and request.user.email:
                orden.email = request.user.email
            if carro.cupon:
                orden.cupon = carro.cupon
                orden.descuento = carro.cupon.descuento
            orden.save()
            # Crear items desde el carrito.
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


@staff_member_required
def detalle_orden_admin(request, id_orden):
    orden = get_object_or_404(Orden, id=id_orden)
    return render(
        request, 'admin/ordenes/orden/detalle.html', {'orden': orden}
    )


@staff_member_required
def orden_admin_pdf(request, id_orden):
    orden = get_object_or_404(Orden, id=id_orden)
    html = render_to_string('ordenes/orden/pdf.html', {'orden': orden})
    respuesta = HttpResponse(content_type='application/pdf')
    respuesta['Content-Disposition'] = f'filename=orden_{orden.id}.pdf'
    weasyprint.HTML(string=html).write_pdf(
        respuesta,
        stylesheets=[weasyprint.CSS(finders.find('css/pdf.css'))]
    )
    return respuesta


def orden_creada(request):
    # Vista que muestra la confirmación de orden creada
    return render(request, 'ordenes/orden/creado.html')
