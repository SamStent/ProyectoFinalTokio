from django.shortcuts import get_object_or_404, render
from .models import Categoria, Producto
from carro.forms import FormularioAniadir
from .recomendador import Recomendador
from .models import Categoria, Producto
# from django.utils import translation  ->> Probar las traducciones.



# Vista para mostrar listado de productos
def listado_productos(request, slug_categoria=None):
    # translation.activate('en')  ->> Solo para probar las traducciones.
    categoria = None
    categorias = Categoria.objects.all()
    # Filtra la consulta para que devuelva solo los disponibles
    productos = Producto.objects.filter(disponible=True)
    # Parámetro opcional para filtrar según una categoria dada
    if slug_categoria:
        categoria = get_object_or_404(Categoria, slug=slug_categoria)
        productos = productos.filter(categoria=categoria)
    return render(
        request,
        'tienda/producto/lista.html',
        {
            'categoria': categoria,
            'categorias': categorias,
            'productos': productos
        }
    )


# Vista para mostrar un único producto.
def detalle_producto(request, id, slug):
    producto = get_object_or_404(
        Producto, id=id, slug=slug, disponible=True
    )
    formulario_producto_carro = FormularioAniadir()
    recomendador = Recomendador()
    productos_recomendados = recomendador.sugerencias_para([producto], 4)
    return render(
        request,
        'tienda/producto/detalle.html',
        {
        'producto': producto,
        'formulario_producto_carro': formulario_producto_carro,
        'productos_recomendados': productos_recomendados
        }
    )

def productos_por_categoria(request, categoria_slug):
    categoria = get_object_or_404(Categoria, slug=categoria_slug)
    productos = Producto.objects.filter(categoria=categoria, disponible=True)
    return render(
        request,
        'tienda/lista.html',
        {
            'categoria': categoria,
            'productos': productos
        }
    )
