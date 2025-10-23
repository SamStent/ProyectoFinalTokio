from django.urls import path
from . import views
from . import views_almacen as v
from django.conf import settings
from django.conf.urls.static import static

app_name = 'tienda'

urlpatterns = [
    # Vista del listado completo.
    path('', views.listado_productos, name='listado_productos'),
    # Pattern a vista del listado filtrado por el param. opcional slug_categoria
    path(
        '<slug:slug_categoria>/',
        views.listado_productos,
        name='listado_productos_por_categoria'
    ),
    # Pattern a detalle_producto pasando id y slug por parámetros
    path(
        '<int:id>/<slug:slug>/',
        views.detalle_producto,
        name='detalle_producto'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
