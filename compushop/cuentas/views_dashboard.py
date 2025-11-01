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
    grafico_existencias_por_proveedor,
    grafico_rotacion_productos,
    bloque_alertas_stock,
)
from .forms import ConfiguracionUsuarioForm
from .models import ConfiguracionUsuario
from django.utils.translation import gettext_lazy as _



@login_required
def dashboard_view(request, rol):
    """
    Vista genérica de dashboard para roles: gerencia, ventas y almacén.
    Se diferencia según el parámetro <rol> recibido en la URL.
    """
    user = request.user

    # Si es almacén, no usamos dashboard de métricas: redirigimos al panel operativo
    if rol == "almacen":
        return redirect('cuentas:panel_almacen')

    df = obtener_dataframe_productos()

    metricas = obtener_metricas_activas(user)

    context = {
        "usuario": user,
        "rol": rol,
        "metricas": metricas,
    }

    # Configuración de los dashboard para roles ventas y gerencia.
    if rol == "ventas":
        context.update({
            "titulo_dashboard": "Dashboard de Ventas",
            "grafico_rendimiento_html": grafico_rendimiento_por_proveedor(df) if metricas.get("rendimiento") else "",
            # OJO: el template suele esperar “grafico_precios_html”
            "grafico_precios_html": grafico_precio_medio_por_proveedor(df) if metricas.get("precio_medio") else "",
            "grafico_distribucion_stock_html": grafico_distribucion_stock(df) if metricas.get("distribucion_stock") else "",
        })

    elif rol == "gerencia":
        context.update({
            "titulo_dashboard": "Dashboard de Gerencia",
            "grafico_valor_stock_html": grafico_valor_stock_por_proveedor(df) if metricas.get("valor_stock") else "",
            "grafico_precios_html": grafico_precio_medio_por_proveedor(df) if metricas.get("precio_medio") else "",
            "grafico_distribucion_stock_html": grafico_distribucion_stock(df) if metricas.get("distribucion_stock") else "",
            "grafico_rendimiento_html": grafico_rendimiento_por_proveedor(df) if metricas.get("rendimiento") else "",
            "grafico_rotacion_html": grafico_rotacion_productos(df) if metricas.get("rotacion") else "",            
        })

    else:
        # En caso de rol inválido
        return redirect('cuentas:panel_personal')

    return render(request, "cuentas/dashboard_metricas.html", context)



@login_required
def config_panel(request):
    """
    Vista que permite a cada rol de usuario (gerencia, ventas, almacén)
    configurar las opciones de su dashboard.
    """
    usuario = request.user
    configuracion, creado = ConfiguracionUsuario.objects.get_or_create(usuario=usuario)

    if request.method == "POST":
        form = ConfiguracionUsuarioForm(request.POST, instance=configuracion, usuario=usuario)

        if form.is_valid():
            # Guardar los campos normales (tema, alertas, etc.)
            obj = form.save(commit=False)

            # === Recuperar las métricas seleccionadas del formulario ===
            metricas_form = form.cleaned_data.get("metricas_activas", {}) or {}

            # === Conservar métricas anteriores (por si el rol cambia o faltan claves) ===
            metricas_previas = configuracion.metricas_activas or {}
            metricas_actualizadas = {**metricas_previas, **metricas_form}

            # === Añadir umbral_stock (si existe en POST o anterior) ===
            umbral = request.POST.get("umbral_stock") or metricas_previas.get("umbral_stock", 5)
            try:
                umbral = int(umbral)
            except (TypeError, ValueError):
                umbral = 5
            metricas_actualizadas["umbral_stock"] = umbral

            # Asignar y guardar
            obj.metricas_activas = metricas_actualizadas
            obj.save()

            messages.success(request, _("Configuración actualizada correctamente."))
            return redirect("cuentas:config_panel")
        else:
            messages.error(request, _("El formulario contiene datos erróneos."))
    else:
        form = ConfiguracionUsuarioForm(instance=configuracion, usuario=usuario)

    # Selección dinámica de plantilla por rol
    tipo = getattr(usuario, "rol_personal", "personal").lower()
    template = f"cuentas/config_{tipo}.html"

    context = {
        "form": form,
        "usuario": usuario,
        "configuracion": configuracion,
    }
    return render(request, template, context)


@login_required
@solo_rol('almacen', 'gerencia')
def config_almacen(request):
    user = request.user
    if request.method == "POST":
        modo_oscuro = 'modo_oscuro' in request.POST
        user.preferencias = {"modo_oscuro": modo_oscuro}
        user.save(update_fields=["preferencias"])
        messages.success(request, _("Configuración guardada correctamente."))
        return redirect('cuentas:panel_almacen')

    modo_oscuro = getattr(user, "preferencias", {}).get("modo_oscuro", False)
    return render(request, "cuentas/config_almacen.html", {"modo_oscuro": modo_oscuro})
