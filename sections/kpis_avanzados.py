"""
Sección KPIs Avanzados del Dashboard P&G.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List

from components.metrics import render_metric_card
from components.charts import create_bar_chart, create_radar_chart, create_line_chart
from utils.formatters import format_currency


def render_kpis_avanzados(
    kpis: Dict[str, Dict[str, float]],
    years: List[str],
    year_selected: str,
    compare_year: str
) -> None:
    """
    Renderiza la sección de KPIs Avanzados.

    Args:
        kpis: Diccionario de KPIs
        years: Lista de años
        year_selected: Año principal de análisis
        compare_year: Año de comparación
    """
    st.markdown("## KPIs Avanzados")

    # Calcular KPIs avanzados
    kpis_avanzados = []
    for year in years:
        ing = kpis.get('ingresos', {}).get(year, 0)
        ebit = kpis.get('ebitda', {}).get(year, 0)
        neto = kpis.get('resultado_neto', {}).get(year, 0)
        personal = kpis.get('gastos_personal', {}).get(year, 0)
        aprov = kpis.get('aprovisionamientos', {}).get(year, 0)
        amort = kpis.get('amortizacion', {}).get(year, 0)

        ebitda = ebit + amort  # EBITDA = EBIT + Amortización

        kpis_avanzados.append({
            'Año': year,
            'Ingresos': ing,
            'EBITDA': ebitda,
            'EBIT': ebit,
            'Resultado Neto': neto,
            'Margen Bruto %': ((ing - aprov) / ing * 100) if ing > 0 else 0,
            'Margen EBITDA %': (ebitda / ing * 100) if ing > 0 else 0,
            'Margen EBIT %': (ebit / ing * 100) if ing > 0 else 0,
            'Margen Neto %': (neto / ing * 100) if ing > 0 else 0,
            'Ratio Personal/Ingresos %': (personal / ing * 100) if ing > 0 else 0,
            'Coste por EUR Ingreso': ((aprov + personal) / ing) if ing > 0 else 0
        })

    df_kpis = pd.DataFrame(kpis_avanzados)

    # Mostrar métricas del año seleccionado
    year_data = df_kpis[df_kpis['Año'] == year_selected].iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_metric_card("EBITDA", year_data['EBITDA'])
        st.metric("Margen EBITDA", f"{year_data['Margen EBITDA %']:.1f}%")

    with col2:
        render_metric_card("EBIT", year_data['EBIT'])
        st.metric("Margen EBIT", f"{year_data['Margen EBIT %']:.1f}%")

    with col3:
        st.metric("Margen Bruto", f"{year_data['Margen Bruto %']:.1f}%")
        st.metric("Margen Neto", f"{year_data['Margen Neto %']:.1f}%")

    with col4:
        st.metric("Ratio Personal", f"{year_data['Ratio Personal/Ingresos %']:.1f}%")
        st.metric("Coste por EUR Ingreso", f"{year_data['Coste por EUR Ingreso']:.2f} EUR")

    st.markdown("---")

    # Gráficos de KPIs
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Evolución de Márgenes")

        fig = create_line_chart(
            df_kpis,
            'Año',
            ['Margen Bruto %', 'Margen EBITDA %', 'Margen EBIT %', 'Margen Neto %'],
            height=400,
            colors=['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728']
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### EBITDA vs EBIT vs Resultado Neto")

        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='EBITDA',
            x=df_kpis['Año'],
            y=df_kpis['EBITDA'],
            marker_color='#2ca02c'
        ))
        fig.add_trace(go.Bar(
            name='EBIT',
            x=df_kpis['Año'],
            y=df_kpis['EBIT'],
            marker_color='#ff7f0e'
        ))
        fig.add_trace(go.Bar(
            name='Resultado Neto',
            x=df_kpis['Año'],
            y=df_kpis['Resultado Neto'],
            marker_color='#1f77b4'
        ))

        fig.update_layout(
            height=400,
            barmode='group',
            yaxis_tickformat=',.0f',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)

    # Tabla resumen de KPIs
    st.markdown("### Tabla Resumen de KPIs")

    # Aplicar estilo con manejo de errores para matplotlib
    styled_kpis = df_kpis.style.format({
        'Ingresos': '{:,.0f} €',
        'EBITDA': '{:,.0f} €',
        'EBIT': '{:,.0f} €',
        'Resultado Neto': '{:,.0f} €',
        'Margen Bruto %': '{:.1f}%',
        'Margen EBITDA %': '{:.1f}%',
        'Margen EBIT %': '{:.1f}%',
        'Margen Neto %': '{:.1f}%',
        'Ratio Personal/Ingresos %': '{:.1f}%',
        'Coste por EUR Ingreso': '{:.2f} €'
    })
    try:
        styled_kpis = styled_kpis.background_gradient(subset=['Margen Neto %'], cmap='RdYlGn')
    except Exception:
        pass  # Si matplotlib no está disponible, mostrar sin gradiente

    st.dataframe(styled_kpis, use_container_width=True, hide_index=True)

    # Radar chart de KPIs
    st.markdown("---")
    st.markdown(f"### Radar de KPIs - {year_selected} vs {compare_year}")

    categories = [
        'Margen Bruto',
        'Margen EBITDA',
        'Margen EBIT',
        'Margen Neto',
        'Eficiencia Personal'
    ]

    values_current = [
        year_data['Margen Bruto %'],
        year_data['Margen EBITDA %'],
        year_data['Margen EBIT %'],
        year_data['Margen Neto %'],
        100 - year_data['Ratio Personal/Ingresos %']  # Invertido para que mayor sea mejor
    ]

    year_comp_data = df_kpis[df_kpis['Año'] == compare_year].iloc[0]
    values_compare = [
        year_comp_data['Margen Bruto %'],
        year_comp_data['Margen EBITDA %'],
        year_comp_data['Margen EBIT %'],
        year_comp_data['Margen Neto %'],
        100 - year_comp_data['Ratio Personal/Ingresos %']
    ]

    fig = create_radar_chart(
        categories,
        [
            {'name': year_selected, 'values': values_current, 'color': '#1f77b4'},
            {'name': compare_year, 'values': values_compare, 'color': '#ff7f0e', 'opacity': 0.5}
        ],
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
