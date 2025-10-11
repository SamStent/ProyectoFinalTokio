from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from cuentas.decorators import solo_rol
from cuentas.utils.metricas import obtener_dataframe_productos
from cuentas.utils.graficos import (
    grafico_valor_stock_por_proveedor,
    grafico_precio_medio_por_proveedor,
    grafico_distribucion_stock
)


@login_required
@solo_rol('gerencia')
def dashboard_view(request):
    """
    Muestra el dashboard con métricas para usuarios del rol 'gerencia'.
    """

    df = obtener_dataframe_productos()

    # Enviar al template
    context = {
        'grafico_stock_html': grafico_valor_stock_por_proveedor(df),
        'grafico_precios_html': grafico_precio_medio_por_proveedor(df),
        'grafico_distribucion_html': grafico_distribucion_stock(df),
    }
    return render(request, 'cuentas/dashboard_metricas.html', context)



@login_required
@solo_rol('gerencia', 'almacen', 'ventas')
def config_panel(request):
    """
    Permite la configuración de su panel a cada rol.
    """
    return render(request, 'cuentas/config_panel.html')
