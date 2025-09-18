from django.urls import path
from . import views, webhooks

app_name = 'pagos'

urlpatterns = [
    path('proceso/', views.pago_proceso, name='proceso'),
    path('completado', views.pago_completado, name='completado'),
    path('cancelado', views.pago_cancelado, name='cancelado'),
    path('webhook/', webhooks.stripe_webhook, name='stripe-webhook'),
]
