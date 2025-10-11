from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from functools import wraps


def solo_clientes(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, "tipo_cuenta", None) == "cliente":
            return view_func(request, *args, **kwargs)
        messages.error(request, "Debes iniciar sesión con una cuenta de cliente.")
        return redirect("cuentas:login")
    return wrapper


def solo_personal(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, "tipo_cuenta", None) == "personal":
            return view_func(request, *args, **kwargs)
        messages.error(request, "Acceso restringido al personal de Compushop.")
        return redirect("cuentas:login")
    return wrapper


def solo_rol(*roles_permitidos):
    """
    Decorador para restringir vistas según el rol_personal.
    Permite múltiples roles (por ejemplo, @solo_rol('gerencia', 'almacen'))
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Si el usuario no está autenticado, lo redirige al login
            if not request.user.is_authenticated:
                messages.warning(request, "Debes iniciar sesión para acceder a esta sección.")
                return redirect("cuentas:login")

            # Si no tiene rol o el rol no está permitido, redirige al panel base
            rol = getattr(request.user, "rol_personal", None)
            if rol not in roles_permitidos:
                messages.error(request, "No tienes permiso para acceder a esta sección.")
                return redirect("cuentas:panel_personal")

            # Todo correcto → ejecuta la vista
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def solo_anonimos(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("cuentas:panel_personal")
        return view_func(request, *args, **kwargs)
    return wrapper
