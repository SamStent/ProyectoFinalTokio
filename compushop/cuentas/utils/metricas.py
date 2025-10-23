# tienda/utils/metricas.py
import pandas as pd
from tienda.models import Producto
from cuentas.models import ConfiguracionUsuario


def obtener_dataframe_productos():
    """
    Convierte los productos de la base de datos en un DataFrame con columnas limpias.
    Incluye proveedor y stock, y calcula el valor del stock.
    """
    productos = Producto.objects.select_related("proveedor").values(
        "id",
        "nombre",
        "proveedor__nombre_empresa",  # campo real del proveedor
        "precio",
        "stock",
        "stock_minimo",
        "disponible",
    )

    df = pd.DataFrame(list(productos))

    if df.empty:
        return df

    # Renombrar proveedor
    df = df.rename(columns={"proveedor__nombre_empresa": "proveedor"})

    # Calcular valor de stock dinámicamente
    df["precio"] = pd.to_numeric(df["precio"], errors="coerce").fillna(0)
    df["stock"] = pd.to_numeric(df["stock"], errors="coerce").fillna(0)
    df["valor_stock"] = df["precio"] * df["stock"]

    return df


def calcular_metricas(df):
    """
    Calcula métricas generales y por proveedor.
    """
    # Asegurar tipos numéricos antes de operar
    for col in ['precio', 'stock', 'stock_minimo', 'valor_stock']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    metricas = {}

    # Valor total del stock global
    metricas['valor_total_stock'] = round(df['valor_stock'].sum(), 2)

    # Promedio de precio y stock por proveedor
    metricas['precio_promedio_por_proveedor'] = (
        df.groupby('proveedor', dropna=False)['precio'].mean().round(2).to_dict()
    )
    metricas['stock_total_por_proveedor'] = (
        df.groupby('proveedor', dropna=False)['stock'].sum().to_dict()
    )
    metricas['valor_stock_por_proveedor'] = (
        df.groupby('proveedor', dropna=False)['valor_stock'].sum().round(2).to_dict()
    )

    # Número de productos por proveedor
    metricas['num_productos_por_proveedor'] = (
        df.groupby('proveedor', dropna=False)['nombre'].count().to_dict()
    )

    # Productos bajo stock mínimo
    metricas['productos_bajo_stock_minimo'] = int((df['stock'] <= df['stock_minimo']).sum())

    # Stock total y precio promedio global
    metricas['stock_total_global'] = int(df['stock'].sum())
    metricas['precio_medio_global'] = round(df['precio'].mean(), 2)

    return metricas


def obtener_metricas_activas(usuario):
    """
    Retorna un diccionario con las métricas activas para el usuario.
    Si no tiene una configuración guardada, aplica valores por defecto según su rol.
    """

    # Intentamos recuperar la configuración guardada
    try:
        config = ConfiguracionUsuario.objects.get(usuario=usuario)
        metricas = config.metricas_activas or {}
    except ConfiguracionUsuario.DoesNotExist:
        metricas = {}

    # === Valores por defecto según el rol ===
    defaults_por_rol = {
        "almacen": {
            "existencias": True,
            "rotacion": True,
            "distribucion_stock": True,
            "alertas_stock": True,
            "umbral_stock": 5,
        },
        "ventas": {
            "rendimiento": True,
            "precio_medio": True,
            "distribucion_stock": True,
            "alertas_stock": True,
            "umbral_stock": 5,
        },
        "gerencia": {
            "valor_stock": True,
            "rendimiento": True,
            "precio_medio": True,
            "rotacion": True,
            "distribucion_stock": True,
            "alertas_stock": True,
            "umbral_stock": 5,
        },
    }

    # Rol del usuario (usa lower() por seguridad)
    rol = getattr(usuario, "rol_personal", "").lower()

    # Combinar defaults + configuración guardada
    defaults = defaults_por_rol.get(rol, {})
    defaults.update(metricas)

    return defaults


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
