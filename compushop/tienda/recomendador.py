import redis
from django.conf import settings
from .models import Producto

# Conectar a redis
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

class Recomendador:
    def obtener_clave_producto(self, id):
        return f'producto:{id}:comprado_con'

    def productos_comprados(self, productos):
        # Obtenemos el id de los objetos producto.
        ids_productos = [p.id for p in productos]
        # Iteramos la lista de ids.
        for id_producto in ids_productos:
            # Iteramos otra vez para luego evitar el mismo id.
            for con_id in ids_productos:
                # Obtiene los demás productos comprados con cada producto.
                if id_producto != con_id:
                    # Incrementa la putuación por producto comprado en conjunto
                    r.zincrby(
                        self.obtener_clave_producto(id_producto), 1, con_id
                    )

    def sugerencias_para(self, productos, max_results=6):
        # Obtenemos el id de los objetos producto.
        ids_productos = [p.id for p in productos]
        if len(productos) == 1:
            sugerencias = r.zrange(
                self.obtener_clave_producto(ids_productos[0]), 0, -1, desc=True
            )[:max_results]
        else:
            # Generar clave temporal construída con los ids de los productos
            ids_planos = ''.join([str(id) for id in ids_productos])
            clave_temp = f'tmp_{ids_planos}'
            # Multiles productos, combinar puntuaciones de todos los productos
            # Alamacenar el sorted set resultante en una clave temporal
            claves = [self.obtener_clave_producto(id) for id in ids_productos]
            r.zunionstore(clave_temp, claves)
            # Eliminar ids de los productos para los que se recomienda
            r.zrem(clave_temp, *ids_productos)
            # Obtener los ids por su puntuación, en orden descendente
            sugerencias = r.zrange(
                clave_temp, 0, -1, desc=True
            )[:max_results]
            # Eliminar la clave temporal
            r.delete(clave_temp)
        ids_productos_sugeridos = [int(id) for id in sugerencias]
        # Obtener los productos sugeridos por orden de aparición
        productos_sugeridos = list(
            Producto.objects.filter(id__in=ids_productos_sugeridos)
        )
        productos_sugeridos.sort(
            key=lambda x: ids_productos_sugeridos.index(x.id)
        )
        return productos_sugeridos

    def limpiar_compras(self):
        for id in Producto.objects.values_list('id', flat=True):
            r.delete(self.obtener_clave_producto(id))
