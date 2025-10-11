from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cuentas.decorators import solo_rol
from cuentas.utils.metricas import (
    obtener_dataframe_productos,
    obtener_metricas_activas,
)
from cuentas.utils.graficos import (
    grafico_valor_stock_por_proveedor,
    grafico_precio_medio_por_proveedor,
    grafico_distribucion_stock,
    grafico_rendimiento_por_proveedor,
    grafico_rotacion_productos,
    bloque_alertas_stock,
)
from .forms import ConfiguracionUsuarioForm
from .models import ConfiguracionUsuario
from django.utils.translation import gettext_lazy as _


# ============================================================
# 📊 DASHBOARD PRINCIPAL DE MÉTRICAS (Gerencia, extensible)
# ============================================================
@login_required
@solo_rol("gerencia", "ventas", "almacen")
def dashboard_view(request):
    """
    Muestra el dashboard con métricas dinámicas para cada rol.
    Las métricas visibles dependen de la configuración guardada por el usuario.
    """
    usuario = request.user
    metricas = obtener_metricas_activas(usuario)
    df = obtener_dataframe_productos()

    # Bloques condicionales: solo se generan si están activados en la configuración.
    context = {
        "usuario": usuario,
        "metricas": metricas,

        # Gráficos de stock, precios y distribución (ya existentes)
        "grafico_stock_html": grafico_valor_stock_por_proveedor(df)
        if metricas.get("grafico_stock")
        else None,

        "grafico_precios_html": grafico_precio_medio_por_proveedor(df)
        if metricas.get("grafico_precios")
        else None,

        "grafico_distribucion_html": grafico_distribucion_stock(df)
        if metricas.get("grafico_distribucion")
        else None,

        # Nuevas métricas
        "grafico_rendimiento_html": grafico_rendimiento_por_proveedor(df)
        if metricas.get("rendimiento_proveedor")
        else None,

        "grafico_rotacion_html": grafico_rotacion_productos(df)
        if metricas.get("rotacion_productos")
        else None,

        # Alertas de stock bajo (bloque HTML)
        "alertas_stock_html": bloque_alertas_stock(df)
        if metricas.get("alertas_stock")
        else None,
    }

    return render(request, "cuentas/dashboard_metricas.html", context)


# ============================================================
# ⚙️ CONFIGURACIÓN DEL PANEL
# ============================================================
@login_required
def config_panel(request):
    """
    Vista que permite a cada rol de usuario (gerencia, ventas, almacén)
    configurar las opciones de su dashboard.
    """
    usuario = request.user
    configuracion, creado = ConfiguracionUsuario.objects.get_or_create(usuario=usuario)

    if request.method == "POST":
        form = ConfiguracionUsuarioForm(request.POST, instance=configuracion)
        if form.is_valid():
            form.save()
            messages.success(request, _("Configuración actualizada correctamente."))
            return redirect("cuentas:config_panel")
        else:
            messages.error(request, _("El formulario contiene datos erróneos."))
    else:
        form = ConfiguracionUsuarioForm(instance=configuracion)

    # Selección de plantilla según rol
    tipo = getattr(usuario, "rol_personal", "personal").lower()
    template = f"cuentas/config_{tipo}.html"

    context = {
        "form": form,
        "usuario": usuario,
        "configuracion": configuracion,
    }
    return render(request, template, context)
