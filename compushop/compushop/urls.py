"""
URL configuration for compushop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

urlpatterns = [
    path('i18n/setlang/', set_language, name='set_language'),
    path('rosetta/', include('rosetta.urls')),
]

urlpatterns += i18n_patterns(
        path('admin/', admin.site.urls),
        path('cuentas/', include('cuentas.urls', namespace='cuentas')),
        path('carro/', include('carro.urls', namespace='carro')),
        path('ordenes/', include('ordenes.urls', namespace='ordenes')),
        path('pagos/', include('pagos.urls', namespace='pagos')),
        path('cupones/', include('cupones.urls', namespace='cupones')),
        path('almacen/', include('tienda.urls_almacen', namespace='almacen')),
        path('', include('tienda.urls', namespace='tienda')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
