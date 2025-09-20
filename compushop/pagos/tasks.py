from io import BytesIO
import weasyprint
from celery import shared_task
from django.contrib.staticfiles import finders
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

@shared_task
def pago_completado(id_orden):
    '''
    Tarea que envía un e-mail con la factura PDF tras completar el pago.
    '''
    print(f"\n===> Ejecutando tarea pago_completado para orden ID: {id_orden}")

    # IMPORT LAZY para evitar AppRegistryNotReady
    from ordenes.models import Orden

    try:
        orden = Orden.objects.get(id=id_orden)
    except Orden.DoesNotExist:
        print(f"===> ERROR: La orden con ID {id_orden} no existe.")
        return

    # Preparar correo
    asunto = f'Compushop - Factura no. {orden.id}'
    mensaje = 'Por favor, encuentre adjunta la factura de su reciente compra.'
    email = EmailMessage(
        asunto,
        mensaje,
        'admin@compushop.com',
        [orden.email]
    )

    # Renderizar HTML
    print("===> Renderizando HTML de factura...")
    html = render_to_string('ordenes/orden/pdf.html', {'orden': orden})
    salida = BytesIO()

    # Buscar hoja de estilos
    stylesheet_path = finders.find('css/pdf.css')
    if stylesheet_path:
        print(f"===> Hoja de estilos encontrada: {stylesheet_path}")
        stylesheets = [weasyprint.CSS(stylesheet_path)]
    else:
        print("===> ADVERTENCIA: No se encontró 'static/css/pdf.css'. Se generará sin estilos.")
        stylesheets = None

    # Generar PDF
    try:
        weasyprint.HTML(string=html).write_pdf(salida, stylesheets=stylesheets)
        print("===> PDF generado correctamente.")
    except Exception as e:
        print(f"===> ERROR generando PDF: {e}")
        return

    # Adjuntar y enviar correo
    email.attach(f'orden_{orden.id}.pdf', salida.getvalue(), 'application/pdf')

    try:
        email.send()
        print(f"===> Email enviado correctamente a {orden.email}\n")
    except Exception as e:
        print(f"===> ERROR al enviar email: {e}")
