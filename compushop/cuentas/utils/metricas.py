# tienda/utils/metricas.py
import pandas as pd
from tienda.models import Producto


def obtener_dataframe_productos():
    """
    Extrae los datos de los productos y sus proveedores a un DataFrame de Pandas.
    Convierte todos los valores numéricos a float explícitamente.
    """
    productos = Producto.objects.select_related('proveedor').values(
        'nombre',
        'precio',
        'stock',
        'stock_minimo',
        'proveedor__nombre_empresa',
        'proveedor__descuento',
        'proveedor__iva',
    )

    df = pd.DataFrame.from_records(productos)

    # Renombrar columnas
    df.rename(columns={
        'proveedor__nombre_empresa': 'proveedor',
        'proveedor__descuento': 'descuento',
        'proveedor__iva': 'iva'
    }, inplace=True)

    # Convertir numéricos a float (de forma robusta)
    def convertir_a_float(valor):
        try:
            return float(valor)
        except (TypeError, ValueError):
            return 0.0

    for col in ['precio', 'stock', 'stock_minimo', 'descuento', 'iva']:
        df[col] = df[col].apply(convertir_a_float)

    # Calcular valor del stock y convertir también
    df['valor_stock'] = df.apply(lambda x: x['precio'] * x['stock'], axis=1)
    df['valor_stock'] = df['valor_stock'].apply(convertir_a_float)

    return df


def calcular_metricas(df):
    """
    Calcula métricas generales y por proveedor.
    """
    # Asegurar tipos numéricos antes de operar
    for col in ['precio', 'stock', 'stock_minimo', 'descuento', 'iva', 'valor_stock']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    metricas = {}

    # 🔹 1. Valor total de stock global
    metricas['valor_total_stock'] = round(df['valor_stock'].sum(), 2)

    # 🔹 2. Promedio de precio y stock por proveedor
    metricas['precio_promedio_por_proveedor'] = (
        df.groupby('proveedor', dropna=False)['precio'].mean().round(2).to_dict()
    )
    metricas['stock_total_por_proveedor'] = (
        df.groupby('proveedor', dropna=False)['stock'].sum().to_dict()
    )
    metricas['valor_stock_por_proveedor'] = (
        df.groupby('proveedor', dropna=False)['valor_stock'].sum().round(2).to_dict()
    )

    # 🔹 3. Número de productos por proveedor
    metricas['num_productos_por_proveedor'] = (
        df.groupby('proveedor', dropna=False)['nombre'].count().to_dict()
    )

    # 🔹 4. Productos bajo stock mínimo
    metricas['productos_bajo_stock_minimo'] = int((df['stock'] <= df['stock_minimo']).sum())

    # 🔹 5. Stock total y precio promedio global
    metricas['stock_total_global'] = int(df['stock'].sum())
    metricas['precio_medio_global'] = round(df['precio'].mean(), 2)

    # 🔹 6. IVA y descuento promedio por proveedor
    metricas['iva_promedio_por_proveedor'] = (
        df.groupby('proveedor', dropna=False)['iva'].mean().round(2).to_dict()
    )
    metricas['descuento_promedio_por_proveedor'] = (
        df.groupby('proveedor', dropna=False)['descuento'].mean().round(2).to_dict()
    )

    return metricas
