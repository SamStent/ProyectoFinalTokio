# tienda/utils/metricas.py
import pandas as pd
from tienda.models import Producto
from cuentas.models import ConfiguracionUsuario


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


def obtener_metricas_activas(usuario):
    """
    Retorna un diccionario con las métricas activas para el usuario.
    En caso de no tener una configuración guardada retorna un diccionario vacío.
    """
    try:
        config = ConfiguracionUsuario.objects.get(usuario=usuario)
        return config.metricas_activas or {}
    except ConfiguracionUsuario.DoesNotExist:
        return {}


# ============================================================
# MÉTRICAS INDIVIDUALES PARA LOS GRÁFICOS DEL DASHBOARD
# ============================================================

import pandas as pd


def metricas_valor_stock(df):
    """
    Valor total del stock por proveedor (para gráfico de barras).
    """
    if df.empty:
        return pd.DataFrame(columns=["proveedor", "valor_stock"])
    return df.groupby("proveedor", as_index=False)["valor_stock"].sum()


def metricas_precio_medio(df):
    """
    Precio medio por proveedor (para gráfico de líneas).
    """
    if df.empty:
        return pd.DataFrame(columns=["proveedor", "precio_medio"])
    return df.groupby("proveedor", as_index=False)["precio"].mean().rename(
        columns={"precio": "precio_medio"}
    )


def metricas_rendimiento_proveedor(df):
    """
    Rendimiento: ratio stock/precio medio por proveedor.
    """
    if df.empty:
        return pd.DataFrame(columns=["proveedor", "rendimiento"])
    df["rendimiento"] = df["stock"] / df["precio"].replace(0, pd.NA)
    return df.groupby("proveedor", as_index=False)["rendimiento"].mean()


def metricas_rotacion_productos(df):
    """
    Rotación estimada (inversa del stock).
    """
    if df.empty:
        return pd.DataFrame(columns=["nombre", "rotacion"])
    df["rotacion"] = 1 / df["stock"].replace(0, pd.NA)
    return df[["nombre", "rotacion"]].dropna()


def metricas_alertas_stock(df, umbral=None):
    """
    Devuelve productos con stock por debajo del mínimo o de un umbral.
    """
    if df.empty:
        return pd.DataFrame(columns=["nombre", "stock"])
    if umbral is not None:
        return df[df["stock"] < umbral][["nombre", "stock"]]
    return df[df["stock"] < df["stock_minimo"]][["nombre", "stock"]]
