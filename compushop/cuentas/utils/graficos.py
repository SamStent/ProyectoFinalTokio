# tienda/utils/graficos.py
import plotly.express as px
import plotly.io as pio
import pandas as pd

def grafico_valor_stock_por_proveedor(df):
    """
    Gráfico de barras horizontales que muestra el valor total
    del stock por proveedor.
    """
    fig = px.bar(
        df.groupby('proveedor', as_index=False)['valor_stock'].sum(),
        x='valor_stock',
        y='proveedor',
        orientation='h',
        title='Valor total de stock por proveedor (€)',
        labels={'valor_stock': 'Valor (€)', 'proveedor': 'Proveedor'},
        text_auto='.2s'
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return pio.to_html(fig, full_html=False)


def grafico_precio_medio_por_proveedor(df):
    """
    Gráfico de barras verticales con el precio medio de los
    productos por proveedor.
    """
    fig = px.bar(
        df.groupby('proveedor', as_index=False)['precio'].mean(),
        x='proveedor',
        y='precio',
        title='Precio medio por proveedor (€)',
        labels={'precio': 'Precio medio (€)', 'proveedor': 'Proveedor'},
        text_auto='.2f'
    )
    fig.update_layout(xaxis_tickangle=-45)
    return pio.to_html(fig, full_html=False)


def grafico_distribucion_stock(df):
    """
    Gráfico de pastel que muestra la distribución porcentual
    del stock por proveedor.
    """
    df_stock = df.groupby('proveedor', as_index=False)['stock'].sum()
    fig = px.pie(
        df_stock,
        values='stock',
        names='proveedor',
        title='Distribución porcentual del stock por proveedor',
        hole=0.4  # gráfico tipo donut
    )
    return pio.to_html(fig, full_html=False)
