from celery import shared_task
from django.core.mail import send_mail
from .models import Orden

@shared_task(name="ordenes.tasks.task_orden_creada")
def task_orden_creada(id_orden):
    from .models import Orden
    """
    Task para enviar un e-mail de notificación cuando una orden
    es creada con éxito.
    """
    orden = Orden.objects.get(id=id_orden)
    asunto = f'Orden Nro. {id.orden}'
    mensaje = (
        f'Estimado {orden.nombre}, \n\n'
        f'Su orden a sido confirmada con éxito.'
        f'El identificador de su orden es {id.orden}'
    )
    correo_enviado = send_mail(
        asunto, mensaje, 'admin@compushop.com', [orden.email]
    )
    return correo_enviado
