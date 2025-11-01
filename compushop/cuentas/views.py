from django.shortcuts import render, redirect
from django.db.models import F
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.contrib import messages
from django.urls import reverse
from .forms import RegistroClienteForm
from .decorators import solo_clientes, solo_personal, solo_rol, solo_anonimos
from ordenes.models import Orden
from tienda.models import Producto


@solo_anonimos
def registro(request):
    if request.method == 'POST':
        formulario = RegistroClienteForm(request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            messages.success(request, "Tu cuenta ha sido creada correctamente. Ya puedes iniciar sesión.")
            return redirect('cuentas:login')
    else:
        formulario = RegistroClienteForm()
    return render(request, 'cuentas/registro.html', {'formulario': formulario})


@login_required
@solo_clientes
def panel_cliente(request):
    """Panel de usuario para clientes autenticados."""
    usuario = request.user
    ordenes = Orden.objects.filter(usuario=usuario).order_by('-creado')[:5]
    return render(request, 'cuentas/panel_cliente.html', {
        'usuario': usuario,
        'ordenes': ordenes,
    })


@login_required
@solo_personal
def panel_personal(request):
    return render(request, 'cuentas/personal_dashboard.html')


@login_required
@solo_rol('almacen', 'gerencia')
def panel_almacen(request):
    from tienda.models import Producto
    alertas = Producto.objects.filter(stock__lte=F('stock_minimo')).order_by('stock')
    return render(request, 'cuentas/almacen.html', {'alertas': alertas})


@login_required
@solo_rol('ventas', 'gerencia')
def panel_ventas(request):
    """
    Panel principal para el rol Ventas.
    Muestra un resumen básico y una métrica por defecto (redimiento
    por proveedor.)
    """
    from cuentas.utils.metricas import obtener_dataframe_productos
    from cuentas.utils.graficos import grafico_rendimiento_por_proveedor

    df = obtener_dataframe_productos()
    grafico_html = grafico_rendimiento_por_proveedor(df)

    context = {
        'grafico_html': grafico_html,
    }

    return render(request, 'cuentas/ventas.html', context)


@login_required
@solo_rol('gerencia')
def panel_gerencia(request):
    return render(request, 'cuentas/gerencia.html', context)


class CustomLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        # Redirección según el tipo de cuenta.
        if user.tipo_cuenta == 'personal':
            return '/cuentas/personal/'
        else:
            return '/cuentas/panel/cliente/'


def logout_usuario(request):
    """
    Cierra la sesión del usuario y redirige al listado de productos.
    """
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    # Redirección respetando prefijo de idioma.
    return redirect(reverse('tienda:listado_productos'))


@login_required
@solo_rol('ventas', 'gerencia')
def inventario_acceso_ventas(request):
    """
    Permite al rol ventas acceder al inventario (vista almacén)
    solo en modo lectura.
    """

    qs = Producto.objects.all().select_related('proveedor').order_by('nombre')
    alertas = qs.filter(stock__lte=F('stock_minimo')).order_by('stock')
    print("Productos encontrados:", qs.count())
    context = {
        'producto': qs,
        'alertas': alertas,
        'modo_lectura': True,
    }

    return render(
        request,
        'tienda/almacen_inventario_list.html',
        context
    )
