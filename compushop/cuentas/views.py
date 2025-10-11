from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from .forms import RegistroClienteForm
from .decorators import solo_clientes, solo_personal, solo_rol, solo_anonimos

# Create your views here.

@solo_anonimos
def registro(request):
    if request.method == 'POST':
        formulario = RegistroClienteForm(request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            return redirect('login')
    else:
        formulario = RegistroClienteForm()
    return render(request, 'cuentas/registro.html', {'formulario': formulario})


@login_required
@solo_clientes
def perfil(request):
    return render(request, 'cuentas/perfil.html')


@login_required
@solo_personal
def panel_personal(request):
    return render(request, 'cuentas/personal_dashboard.html')


@login_required
@solo_rol('almacen', 'gerencia')
def panel_almacen(request):
    return render(request, 'cuentas/almacen.html')


@login_required
@solo_rol('ventas', 'gerencia')
def panel_ventas(request):
    return render(request, 'cuentas/ventas.html')


@login_required
@solo_rol('gerencia')
def panel_gerencia(request):
    return render(request, 'cuentas/gerencia.html')


class CustomLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        # Redirección según el tipo de cuenta.
        if user.tipo_cuenta == 'personal':
            return '/cuentas/personal/'
        else:
            return '/cuentas/perfil/'
