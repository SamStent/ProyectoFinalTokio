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
    except ValueError:
        print("❌ Error en el payload (no es JSON válido)")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print("❌ Error en la firma del webhook:", e)
        return HttpResponse(status=400)

    # --- CASO 1: Checkout completado correctamente ---
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Solo si se trata de un pago directo y fue exitoso
        if session.get('mode') == 'payment' and session.get('payment_status') == 'paid':
            try:
                orden_id = session.get('client_reference_id')
                if not orden_id:
                    print("⚠️ No se encontró client_reference_id en la sesión.")
                    return HttpResponse(status=400)

                orden = Orden.objects.get(id=orden_id)

                # Marcar la orden como pagada si no lo estaba ya
                if not orden.pagado:
                    orden.pagado = True
                    orden.stripe_id = session.get('payment_intent')
                    # Si la orden no tiene usuario y la sesión trae un email coincidente, asociar
                    if not orden.usuario and session.get('customer_details'):
                        email_cliente = session['customer_details'].get('email')
                        if email_cliente:
                            from django.contrib.auth import get_user_model
                            User = get_user_model()
                            u = User.objects.filter(email=email_cliente).first()
                            if u:
                                orden.usuario = u
                    orden.save(update_fields=['pagado', 'stripe_id', 'usuario'])

                    # Recomendaciones y tareas asincrónicas
                    ids_productos = orden.items.values_list('id_producto', flat=True)
                    productos = Producto.objects.filter(id__in=ids_productos)
                    r = Recomendador()
                    r.productos_comprados(productos)

                    pago_completado.delay(orden.id)
                    print(f"✅ Orden {orden.id} marcada como pagada correctamente.")

            except Orden.DoesNotExist:
                print("❌ No se encontró la orden asociada al webhook.")
                return HttpResponse(status=404)

    # --- CASO 2 (opcional): PaymentIntent manual (seguridad extra) ---
    elif event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        orden_id = payment_intent['metadata'].get('orden_id')
        if orden_id:
            from ordenes.models import Orden
            orden = Orden.objects.filter(id=orden_id).first()
            if orden and not orden.pagado:
                orden.pagado = True
                orden.stripe_id = payment_intent['id']
                orden.save(update_fields=['pagado', 'stripe_id'])
                print(f"✅ Orden {orden.id} actualizada por payment_intent.succeeded.")

    return HttpResponse(status=200)
