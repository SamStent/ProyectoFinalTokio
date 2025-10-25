from .models import Categoria


def categorias_disponibles(request):
    """
    Devuelve todas las categorías activas para mostrarlas en el menú principal.
    """

    return {
        'categorias_menu': Categoria.objects.filter(activo=True)
    }
