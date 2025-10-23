# tienda/utils/graficos.py
import plotly.express as px
import plotly.io as pio
import pandas as pd
from plotly.offline import plot


# ============================================================
# 📊 GRÁFICOS PRINCIPALES
# ============================================================

def grafico_valor_stock_por_proveedor(df):
    """
    Gráfico de barras horizontales que muestra el valor total
    del stock por proveedor.
    """
    if df.empty:
        return "<p>No hay datos de stock disponibles.</p>"

    fig = px.bar(
        df.groupby('proveedor', as_index=False)['valor_stock'].sum(),
        x='valor_stock',
        y='proveedor',
        orientation='h',
        title='Valor total de stock por proveedor (€)',
        labels={'valor_stock': 'Valor (€)', 'proveedor': 'Proveedor'},
        text_auto='.2s'
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        template="plotly_white"
    )
    return pio.to_html(fig, full_html=False)


def grafico_precio_medio_por_proveedor(df):
    """
    Gráfico de barras verticales con el precio medio de los
    productos por proveedor.
    """
    if df.empty:
        return "<p>No hay datos de precios disponibles.</p>"

    fig = px.bar(
        df.groupby('proveedor', as_index=False)['precio'].mean(),
        x='proveedor',
        y='precio',
        title='Precio medio por proveedor (€)',
        labels={'precio': 'Precio medio (€)', 'proveedor': 'Proveedor'},
        text_auto='.2f'
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        template="plotly_white"
    )
    return pio.to_html(fig, full_html=False)


def grafico_distribucion_stock(df):
    """
    Gráfico de pastel (donut) con la distribución porcentual
    del stock por proveedor.
    """
    if df.empty:
        return "<p>No hay datos de stock disponibles.</p>"

    df_stock = df.groupby('proveedor', as_index=False)['stock'].sum()
    fig = px.pie(
        df_stock,
        values='stock',
        names='proveedor',
        title='Distribución porcentual del stock por proveedor',
        hole=0.4
    )
    fig.update_traces(textinfo='percent+label')
    fig.update_layout(template="plotly_white")
    return pio.to_html(fig, full_html=False)


# ============================================================
# 🔍 GRÁFICOS ADICIONALES DEL DASHBOARD
# ============================================================

def grafico_rendimiento_por_proveedor(df):
    """
    Gráfico de rendimiento (stock/precio medio) por proveedor.
    """
    if df.empty:
        return "<p>No hay datos de rendimiento disponibles.</p>"

    df['rendimiento'] = df['stock'] / df['precio'].replace(0, pd.NA)
    data = df.groupby('proveedor', as_index=False)['rendimiento'].mean()

    fig = px.bar(
        data,
        x='proveedor',
        y='rendimiento',
        title='Rendimiento por proveedor (Stock / Precio medio)',
        labels={'rendimiento': 'Rendimiento', 'proveedor': 'Proveedor'},
        color='rendimiento',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(template="plotly_white")
    return pio.to_html(fig, full_html=False)


def grafico_rotacion_productos(df):
    """
    Gráfico de rotación de productos (inversa del stock).
    """
    if df.empty:
        return "<p>No hay datos de rotación disponibles.</p>"

    df['rotacion'] = 1 / df['stock'].replace(0, pd.NA)
    data = df[['nombre', 'rotacion']].dropna()

    fig = px.bar(
        data,
        x='nombre',
        y='rotacion',
        title='Rotación estimada de productos',
        labels={'nombre': 'Producto', 'rotacion': 'Rotación (1/Stock)'},
        color='rotacion',
        color_continuous_scale='OrRd'
    )
    fig.update_layout(
        xaxis_tickangle=45,
        template="plotly_white"
    )
    return pio.to_html(fig, full_html=False)


# ============================================================
# ⚠️ ALERTAS DE STOCK BAJO
# ============================================================

def bloque_alertas_stock(df, umbral=5):
    """
    Genera una lista HTML con productos cuyo stock está por debajo del umbral.
    """
    if df.empty:
        return ""

    df_alertas = df[df['stock'] < umbral]
    if df_alertas.empty:
        return "<p>No hay productos con bajo nivel de stock.</p>"

    html = "<ul class='list-group'>"
    for _, row in df_alertas.iterrows():
        html += f"<li class='list-group-item d-flex justify-content-between align-items-center'>"
        html += f"{row['nombre']} <span class='badge bg-danger'>{int(row['stock'])}</span>"
        html += "</li>"
    html += "</ul>"
    return html


def grafico_existencias_por_proveedor(df):
    """
    Gráfico adaptable de existencias por proveedor.
    - Horizontal si hay más de 8 proveedores.
    - Vertical si hay pocos.
    - Scroll automático si hay demasiados registros.
    """

    if df.empty:
        return "<p class='text-muted'>No hay datos disponibles para existencias.</p>"

    columnas = [c.lower() for c in df.columns]
    df.columns = columnas

    if "proveedor" not in columnas or "stock" not in columnas:
        return "<p class='text-danger'>El DataFrame no contiene 'proveedor' o 'stock'.</p>"

    existencias = (
        df.groupby("proveedor")["stock"]
        .sum()
        .reset_index()
        .sort_values("stock", ascending=False)
    )

    total = existencias["stock"].sum()
    if total == 0:
        return "<p class='text-warning'>No hay unidades registradas en stock actualmente.</p>"

    # --- orientación automática ---
    orientation = "h" if len(existencias) > 8 else "v"

    # --- gráfico principal ---
    fig = px.bar(
        existencias,
        x="stock" if orientation == "h" else "proveedor",
        y="proveedor" if orientation == "h" else "stock",
        orientation=orientation,
        title="Existencias por proveedor",
        text="stock",
        labels={"proveedor": "Proveedor", "stock": "Unidades en stock"},
    )

    fig.update_traces(
    texttemplate="%{y}" if orientation == "h" else "%{y}",  # muestra número fijo
    textposition="inside",       # texto fuera de la barra
    textfont=dict(size=12, color="black"),  # tamaño y color
    insidetextanchor="start",     # alineación del texto
    cliponaxis=False,
    marker_color="#2ecc71",
    marker_line_color="#145a32",
    marker_line_width=1.2,
)

    # --- layout adaptado ---
    if orientation == "h":
        fig.update_layout(
            yaxis=dict(
                title=None,
                automargin=True,
                categoryorder="total ascending",
                tickfont=dict(size=11),
            ),
            xaxis=dict(title="Unidades"),
            margin=dict(l=180, r=40, t=60, b=40),
            height=650,  # altura fija
        )
    else:
        fig.update_layout(
            xaxis=dict(title=None, tickangle=-45, automargin=True),
            yaxis=dict(title="Unidades"),
            margin=dict(l=60, r=40, t=60, b=160),
            height=500,
        )

    fig.update_layout(
        title_x=0.5,
        title_font_size=20,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", size=13),
        showlegend=False,
    )

    # --- scroll automático dentro de la card ---
    html_div = plot(fig, output_type="div", include_plotlyjs=True)
    html_wrapped = (
        "<div style='overflow-y:auto; max-height:650px; width:100%; "
        "padding:10px; box-sizing:border-box;'>"
        f"{html_div}</div>"
    )
    return html_wrapped
