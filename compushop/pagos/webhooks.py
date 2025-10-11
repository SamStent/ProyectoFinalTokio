import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ordenes.models import Orden
from .tasks import pago_completado
from tienda.models import Producto
from tienda.recomendador import Recomendador

'''
Going live:
    Once you have tested your integration, you can apply for a production
    Stripe account. When you are ready to move into production, remember
    to replace your test Stripe credentials with the live ones in the
    settings.py file. You will also need to add a webhook endpoint for
    your hosted website at https://dashboard.stripe.com/webhooks instead
    of using the Stripe CLI. Chapter 17, Going Live, will teach you how to
    configure project settings for multiple environments.
'''


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        print("Error en el payload")
        # Carga de pago no válida
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print("Error en la firma del webhook:", e)
        # Signature no válida
        return HttpResponse(status=400)
    if event.type == 'checkout.session.completed':
        session = event.data.object
        if (
            session.mode == 'payment'
            and session.payment_status == 'paid'
        ):
            try:
                orden = Orden.objects.get(
                    id=session.client_reference_id
                )
                # Marcar orden como pagada
                if not orden.pagado:
                    orden.pagado = True
                    # Almacena el ID de pago de Stripe
                    orden.stripe_id = session.payment_intent
                    orden.save()
                    # Guardar los productos comprados para las recomendaciones
                    ids_productos = orden.items.values_list('id_producto')
                    productos =  Producto.objects.filter(id__in=ids_productos)
                    r = Recomendador()
                    r.productos_comprados(productos)
                    # Iniciar asynchronous task.
                    pago_completado.delay(orden.id)
            except Orden.DoesNotExist:
                return HttpResponse(status=404)

    return HttpResponse(status=200)
