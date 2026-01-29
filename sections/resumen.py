"""
Sección Resumen Ejecutivo del Dashboard P&G.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List

from components.metrics import render_metric_row
from components.charts import create_evolution_chart, create_pie_chart, create_bar_chart
from utils.formatters import format_currency, calculate_variation


def render_resumen(
    kpis: Dict[str, Dict[str, float]],
    years: List[str],
    year_selected: str,
    compare_year: str
) -> None:
    """
    Renderiza la sección de Resumen Ejecutivo.

    Args:
        kpis: Diccionario de KPIs
        years: Lista de años
        year_selected: Año principal de análisis
        compare_year: Año de comparación
    """
    st.markdown("## Resumen Ejecutivo")

    # KPIs principales
    ingresos_actual = kpis.get('ingresos', {}).get(year_selected, 0)
    ingresos_anterior = kpis.get('ingresos', {}).get(compare_year, 0)
    ebitda_actual = kpis.get('ebitda', {}).get(year_selected, 0)
    ebitda_anterior = kpis.get('ebitda', {}).get(compare_year, 0)
    resultado_actual = kpis.get('resultado_neto', {}).get(year_selected, 0)
    resultado_anterior = kpis.get('resultado_neto', {}).get(compare_year, 0)

    margen_actual = (resultado_actual / ingresos_actual * 100) if ingresos_actual else 0
    margen_anterior = (resultado_anterior / ingresos_anterior * 100) if ingresos_anterior else 0

    render_metric_row([
        {
            'label': 'Ingresos Netos',
            'value': ingresos_actual,
            'previous_value': ingresos_anterior,
            'format_type': 'currency',
            'icon': ''
        },
        {
            'label': 'EBIT',
            'value': ebitda_actual,
            'previous_value': ebitda_anterior,
            'format_type': 'currency',
            'icon': ''
        },
        {
            'label': 'Resultado Neto',
            'value': resultado_actual,
            'previous_value': resultado_anterior,
            'format_type': 'currency',
            'icon': ''
        },
        {
            'label': 'Margen Neto',
            'value': margen_actual,
            'previous_value': margen_anterior,
            'format_type': 'percentage',
            'icon': ''
        },
    ], compare_year)

    st.markdown("---")

    # Gráficos principales
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Evolución de Resultados")

        data_evolucion = {
            'Ingresos': [kpis.get('ingresos', {}).get(y, 0) for y in years],
            'EBIT': [kpis.get('ebitda', {}).get(y, 0) for y in years],
            'Resultado Neto': [kpis.get('resultado_neto', {}).get(y, 0) for y in years]
        }

        fig = create_evolution_chart(data_evolucion, years, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"### Distribución de Costes {year_selected}")

        costes = {
            'Aprovisionamientos': kpis.get('aprovisionamientos', {}).get(year_selected, 0),
            'Personal': kpis.get('gastos_personal', {}).get(year_selected, 0),
            'Otros Gastos': kpis.get('otros_gastos', {}).get(year_selected, 0),
            'Amortización': kpis.get('amortizacion', {}).get(year_selected, 0),
            'Gastos Financieros': kpis.get('gastos_financieros', {}).get(year_selected, 0)
        }

        fig = create_pie_chart(
            labels=list(costes.keys()),
            values=list(costes.values()),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    # Segunda fila de gráficos
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Márgenes por Año")

        margenes_data = []
        for year in years:
            ing = kpis.get('ingresos', {}).get(year, 0)
            ebit = kpis.get('ebitda', {}).get(year, 0)
            neto = kpis.get('resultado_neto', {}).get(year, 0)

            margenes_data.append({
                'Año': year,
                'Margen EBIT': (ebit / ing * 100) if ing > 0 else 0,
                'Margen Neto': (neto / ing * 100) if ing > 0 else 0
            })

        df_margenes = pd.DataFrame(margenes_data)

        fig = create_bar_chart(
            df_margenes, 'Año',
            ['Margen EBIT', 'Margen Neto'],
            height=350,
            colors=['#2ca02c', '#ff7f0e']
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Crecimiento Interanual")

        crecimientos = []
        for i, year in enumerate(years[1:], 1):
            prev_year = years[i-1]
            ing_act = kpis.get('ingresos', {}).get(year, 0)
            ing_ant = kpis.get('ingresos', {}).get(prev_year, 0)
            neto_act = kpis.get('resultado_neto', {}).get(year, 0)
            neto_ant = kpis.get('resultado_neto', {}).get(prev_year, 0)

            crecimientos.append({
                'Período': f"{prev_year}-{year}",
                'Crecimiento Ingresos': calculate_variation(ing_act, ing_ant),
                'Crecimiento Resultado': calculate_variation(neto_act, neto_ant)
            })

        df_crec = pd.DataFrame(crecimientos)

        fig = create_bar_chart(
            df_crec, 'Período',
            ['Crecimiento Ingresos', 'Crecimiento Resultado'],
            height=350,
            colors=['#1f77b4', '#d62728']
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig, use_container_width=True)
