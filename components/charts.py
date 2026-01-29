"""
Componentes de gráficos para el Dashboard P&G.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict, Optional, Any
from utils.formatters import format_currency


def create_evolution_chart(
    data: Dict[str, List[float]],
    years: List[str],
    title: str = "",
    height: int = 400,
    show_bars: bool = True,
    show_lines: bool = True
) -> go.Figure:
    """
    Crea un gráfico de evolución temporal.

    Args:
        data: Diccionario con series de datos {nombre: [valores]}
        years: Lista de años
        title: Título del gráfico
        height: Altura en píxeles
        show_bars: Mostrar barras para primera serie
        show_lines: Mostrar líneas para resto de series

    Returns:
        Figura de Plotly
    """
    fig = go.Figure()

    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd']

    for i, (name, values) in enumerate(data.items()):
        if i == 0 and show_bars:
            fig.add_trace(go.Bar(
                name=name,
                x=years,
                y=values,
                marker_color=colors[i % len(colors)],
                text=[format_currency(v) for v in values],
                textposition='outside'
            ))
        elif show_lines:
            fig.add_trace(go.Scatter(
                name=name,
                x=years,
                y=values,
                mode='lines+markers+text',
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=10),
                text=[format_currency(v) for v in values],
                textposition='top center'
            ))

    fig.update_layout(
        title=title,
        height=height,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_tickformat=',.0f',
        hovermode='x unified'
    )

    return fig


def create_pie_chart(
    labels: List[str],
    values: List[float],
    title: str = "",
    height: int = 400,
    hole: float = 0.4,
    show_total: bool = True,
    colors: Optional[List[str]] = None
) -> go.Figure:
    """
    Crea un gráfico de pastel/donut.

    Args:
        labels: Etiquetas
        values: Valores
        title: Título del gráfico
        height: Altura en píxeles
        hole: Tamaño del agujero (0 para pie, >0 para donut)
        show_total: Mostrar total en el centro
        colors: Lista de colores personalizados

    Returns:
        Figura de Plotly
    """
    if colors is None:
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#dfe6e9']

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=hole,
        marker_colors=colors[:len(labels)],
        textinfo='percent+label',
        textposition='outside',
        pull=[0.05 if i < 2 else 0 for i in range(len(labels))]
    )])

    annotations = []
    if show_total and hole > 0:
        total = sum(values)
        annotations.append(dict(
            text=f'Total<br>{format_currency(total)}',
            x=0.5, y=0.5,
            font_size=14,
            showarrow=False
        ))

    fig.update_layout(
        title=title,
        height=height,
        annotations=annotations,
        showlegend=False
    )

    return fig


def create_bar_chart(
    data: pd.DataFrame,
    x: str,
    y: List[str],
    title: str = "",
    height: int = 400,
    barmode: str = 'group',
    orientation: str = 'v',
    show_text: bool = True,
    colors: Optional[List[str]] = None
) -> go.Figure:
    """
    Crea un gráfico de barras.

    Args:
        data: DataFrame con los datos
        x: Columna para eje X
        y: Lista de columnas para eje Y
        title: Título del gráfico
        height: Altura en píxeles
        barmode: 'group' o 'stack'
        orientation: 'v' vertical, 'h' horizontal
        show_text: Mostrar valores en las barras
        colors: Lista de colores personalizados

    Returns:
        Figura de Plotly
    """
    if colors is None:
        colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd']

    fig = go.Figure()

    for i, col in enumerate(y):
        x_vals = data[x] if orientation == 'v' else data[col]
        y_vals = data[col] if orientation == 'v' else data[x]

        text = None
        if show_text:
            if orientation == 'v':
                text = [format_currency(v) if abs(v) >= 1000 else f"{v:.1f}%" for v in data[col]]
            else:
                text = [format_currency(v) for v in data[col]]

        fig.add_trace(go.Bar(
            name=col,
            x=x_vals,
            y=y_vals,
            orientation=orientation,
            marker_color=colors[i % len(colors)],
            text=text,
            textposition='outside' if orientation == 'v' else 'auto'
        ))

    fig.update_layout(
        title=title,
        height=height,
        barmode=barmode,
        showlegend=len(y) > 1,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        yaxis_tickformat=',.0f' if orientation == 'v' else None,
        xaxis_tickformat=',.0f' if orientation == 'h' else None
    )

    return fig


def create_waterfall_chart(
    labels: List[str],
    values: List[float],
    measures: List[str],
    title: str = "",
    height: int = 500
) -> go.Figure:
    """
    Crea un gráfico waterfall.

    Args:
        labels: Etiquetas de cada barra
        values: Valores de cada barra
        measures: Tipo de cada barra ('absolute', 'relative', 'total')
        title: Título del gráfico
        height: Altura en píxeles

    Returns:
        Figura de Plotly
    """
    fig = go.Figure(go.Waterfall(
        name="",
        orientation="v",
        measure=measures,
        x=labels,
        textposition="outside",
        text=[format_currency(v) for v in values],
        y=values,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#2ca02c"}},
        decreasing={"marker": {"color": "#d62728"}},
        totals={"marker": {"color": "#1f77b4"}}
    ))

    fig.update_layout(
        title=title,
        height=height,
        showlegend=False,
        yaxis_tickformat=',.0f'
    )

    return fig


def create_radar_chart(
    categories: List[str],
    values_list: List[Dict[str, Any]],
    title: str = "",
    height: int = 500
) -> go.Figure:
    """
    Crea un gráfico radar.

    Args:
        categories: Lista de categorías
        values_list: Lista de diccionarios con 'name', 'values', 'color'
        title: Título del gráfico
        height: Altura en píxeles

    Returns:
        Figura de Plotly
    """
    fig = go.Figure()

    for item in values_list:
        fig.add_trace(go.Scatterpolar(
            r=item['values'],
            theta=categories,
            fill='toself',
            name=item['name'],
            line_color=item.get('color', '#1f77b4'),
            opacity=item.get('opacity', 1)
        ))

    max_val = max(max(item['values']) for item in values_list)

    fig.update_layout(
        title=title,
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max_val * 1.1])
        ),
        showlegend=True,
        height=height
    )

    return fig


def create_line_chart(
    data: pd.DataFrame,
    x: str,
    y: List[str],
    title: str = "",
    height: int = 400,
    colors: Optional[List[str]] = None
) -> go.Figure:
    """
    Crea un gráfico de líneas.

    Args:
        data: DataFrame con los datos
        x: Columna para eje X
        y: Lista de columnas para eje Y
        title: Título del gráfico
        height: Altura en píxeles
        colors: Lista de colores personalizados

    Returns:
        Figura de Plotly
    """
    if colors is None:
        colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728']

    fig = go.Figure()

    for i, col in enumerate(y):
        fig.add_trace(go.Scatter(
            x=data[x],
            y=data[col],
            name=col,
            mode='lines+markers',
            line=dict(width=3, color=colors[i % len(colors)]),
            marker=dict(size=10)
        ))

    fig.update_layout(
        title=title,
        height=height,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        hovermode='x unified',
        yaxis_title='Porcentaje (%)'
    )

    return fig
