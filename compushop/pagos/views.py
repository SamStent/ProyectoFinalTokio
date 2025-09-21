from decimal import Decimal
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from ordenes.models import Orden

# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

def pago_proceso(request):
    id_orden = request.session.get('id_orden')
    orden = get_object_or_404(Orden, id=id_orden)
    if request.method == 'POST':
        success_url = request.build_absolute_uri(
            reverse('pagos:completado')
        )
        cancel_url = request.build_absolute_uri(
            reverse('pagos:cancelado')
        )
        # Datos de la sesión de pago de Stripe
        session_data = {
            'mode': 'payment',
            'client_reference_id': orden.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }
        # Añadir los productos de la orden a la sesión de pago de Stripe
        for item in orden.items.all():
            session_data['line_items'].append(
                {
                    'price_data': {
                        'unit_amount': int(item.precio * Decimal('100')),
                        'currency': 'usd',
                        'product_data': {
                            'name': item.producto.nombre,
                        },
                    },
                    'quantity': item.cantidad,
                }
            )
        # Cupon stripe
        if orden.cupon:
            cupon_stripe = stripe.Coupon.create(
                name=orden.cupon.codigo,
                percent_off=orden.descuento,
                duration='once'
            )
            session_data['discounts'] = [{'coupon': cupon_stripe.id}]
        # Crear la sesión de pago de Stripe
        session = stripe.checkout.Session.create(**session_data)
        # Redirigir al formulario de pago de Stripe
        return redirect(session.url, code=303)
    else:
        return render(request, 'pagos/proceso.html', locals())


def pago_completado(request):
    return render(request, 'pagos/completado.html')


def pago_cancelado(request):
    return render(request, 'pagos/cancelado.html')
