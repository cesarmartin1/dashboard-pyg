"""
Componentes de métricas para el Dashboard P&G.
"""

import streamlit as st
from typing import Optional
from utils.formatters import format_currency, calculate_variation


def render_metric_card(
    label: str,
    value: float,
    previous_value: Optional[float] = None,
    compare_year: Optional[str] = None,
    format_type: str = "currency",
    icon: str = ""
) -> None:
    """
    Renderiza una tarjeta de métrica.

    Args:
        label: Etiqueta de la métrica
        value: Valor actual
        previous_value: Valor anterior para comparación
        compare_year: Año de comparación
        format_type: Tipo de formato ("currency", "percentage", "number")
        icon: Emoji/icono opcional
    """
    if format_type == "currency":
        formatted_value = format_currency(value)
    elif format_type == "percentage":
        formatted_value = f"{value:.1f}%"
    else:
        formatted_value = f"{value:,.0f}"

    delta = None
    delta_suffix = ""

    if previous_value is not None:
        if format_type == "percentage":
            delta = value - previous_value
            delta_suffix = f" pp vs {compare_year}" if compare_year else " pp"
            delta_str = f"{delta:+.1f}{delta_suffix}"
        else:
            var = calculate_variation(value, previous_value)
            delta_suffix = f"% vs {compare_year}" if compare_year else "%"
            delta_str = f"{var:+.1f}{delta_suffix}"

        st.metric(
            f"{icon} {label}" if icon else label,
            formatted_value,
            delta_str,
            delta_color="normal"
        )
    else:
        st.metric(
            f"{icon} {label}" if icon else label,
            formatted_value
        )


def render_metric_row(
    metrics: list,
    compare_year: Optional[str] = None
) -> None:
    """
    Renderiza una fila de métricas.

    Args:
        metrics: Lista de diccionarios con keys:
            - label: Etiqueta
            - value: Valor actual
            - previous_value: Valor anterior (opcional)
            - format_type: "currency", "percentage", "number"
            - icon: Emoji (opcional)
        compare_year: Año de comparación
    """
    cols = st.columns(len(metrics))

    for col, metric in zip(cols, metrics):
        with col:
            render_metric_card(
                label=metric.get('label', ''),
                value=metric.get('value', 0),
                previous_value=metric.get('previous_value'),
                compare_year=compare_year,
                format_type=metric.get('format_type', 'currency'),
                icon=metric.get('icon', '')
            )
