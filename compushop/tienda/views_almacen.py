from django.db.models import F, Q
from django.contrib.auth.decorators import login_required
from cuentas.decorators import solo_rol
from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto
from .forms import AjusteStockForm

@login_required
@solo_rol('almacen', 'gerencia')
def inventario_list(request):
    qs = Producto.objects.all().select_related('proveedor')
    q = request.GET.get('q') or ''
    filtro = request.GET.get('filtro') or ''
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(sku__icontains=q))
    if filtro == 'bajo':
        qs = qs.filter(stock__lte=F('stock_minimo'))
    elif filtro == 'no_disponible':
        qs = qs.filter(disponible=False)
    qs = qs.order_by('nombre')
    return render(request, 'tienda/almacen_inventario_list.html', {'producto': qs})

@login_required
@solo_rol('almacen', 'gerencia')
def ajustar_stock(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = AjusteStockForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            cantidad = form.cleaned_data['cantidad']
            delta = cantidad if tipo == 'entrada' else (-cantidad if tipo == 'salida' else cantidad)
            producto.ajustar_stock(delta, tipo=tipo, usuario=request.user,
                                   motivo=form.cleaned_data.get('motivo',''),
                                   referencia=form.cleaned_data.get('referencia',''))
            return redirect('almacen:inventario')
    else:
        form = AjusteStockForm()
    return render(request, 'tienda/almacen_ajuste_form.html', {'producto': producto, 'form': form})

@login_required
@solo_rol('almacen', 'gerencia')
def movimientos_list(request):
    from .models import StockMovimiento
    movs = StockMovimiento.objects.select_related('producto','usuario').all()
    q = request.GET.get('q') or ''
    if q:
        movs = movs.filter(Q(producto__nombre__icontains=q) | Q(referencia__icontains=q) | Q(motivo__icontains=q))
    return render(request, 'tienda/almacen_movimientos_list.html', {'movimientos': movs})
