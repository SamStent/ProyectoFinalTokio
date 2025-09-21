from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from tienda.models import Producto
from cupones.models import Cupon


class Carro:
    def __init__(self, request):
        '''
            Inicializa el carro
        '''
        # Almacenamos la sesión haciéndola accesible para los otros métodos
        self.session = request.session
        # Recuperamos el carro si lo hay
        carro = self.session.get(settings.ID_SESSION_CARRO)
        # Si no hay carro creamos uno vacío
        if not carro:
            carro = self.session[settings.ID_SESSION_CARRO] = {}
        # Lo almacenamos en self.carro
        self.carro = carro
        # Almacena en el objeto Carro el cupon actualmente aplicado.
        self.id_cupon = self.session.get('id_cupon')

    def aniadir(self, producto, cantidad=1, actualizar_cantidad=False):
        '''
            Método añadir.
            Parámetros:
                - producto: Instancia de Producto para añadir al Carro.
                - cantidad: int. Por defecto = 1.
                - actualizar_cantidad: bol. actualizar(True) o sumar(False)
                a la cantidad existente.
        '''
        # Django usa JSON para serializar, por eso convertimos el id a string
        id_producto = str(producto.id)
        # Comprobamos si el producto está en el carro
        if id_producto not in self.carro:
            # Añade la clave id_producto al carro, cuyo valor es otro dict
            self.carro[id_producto] = {
                'cantidad': 0,
                'precio': str(producto.precio)
            }
            # Comprueba se hay que acualizar o sumar la cantidad
        if actualizar_cantidad:
            self.carro[id_producto]['cantidad'] = cantidad
        else:
            self.carro[id_producto]['cantidad'] += cantidad
        # Guarda el carro en la sesión
        self.guardar()

    def guardar(self):
        # Marca la session como modificada para asegurarse que se ha guardado
        self.session.modified = True

    def eliminar(self, producto):
        '''
            Elimina un producto del carro.
            Recibe la instancia del producto a eliminar.
        '''
        id_producto = str(producto.id)
        # Comprobamos que el producto está en el carro
        if id_producto in self.carro:
            del self.carro[id_producto]
            self.guardar()

    def __iter__(self):
        '''
            Definición de métdo __iter__(), itera y obtiene los productos
            desde la base de datos.
        '''
        ids_productos = self.carro.keys()
        productos = Producto.objects.filter(id__in=ids_productos)
        carro = self.carro.copy()
        for producto in productos:
            carro[str(producto.id)]['producto'] = producto
        for item in carro.values():
            item['precio'] = Decimal(item['precio'])
            item['precio_total'] = item['precio'] * item['cantidad']
            yield item

    def __len__(self):
        '''
            Cuenta los items del carro
        '''
        return sum(item['cantidad'] for item in self.carro.values())

    def precio_total(self):
        return sum(
            Decimal(item['precio']) * item['cantidad']
            for item in self.carro.values()
        )

    def limpiar(self):
        # Elimina el carro de la sesión
        del self.session[settings.ID_SESSION_CARRO]
        self.guardar()

    @property
    def cupon(self):
        if self.id_cupon:
            try:
                return Cupon.objects.get(id=self.id_cupon)
            except Cupon.DoesNotExist:
                pass
        return None

    def obtener_descuento(self):
        if self.cupon:
            return (
                self.cupon.descuento / Decimal('100')
            ) * self.precio_total()
            return descuento.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return Decimal('0.00')

    def total_con_descuento(self):
        total = self.precio_total() - self.obtener_descuento()
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
