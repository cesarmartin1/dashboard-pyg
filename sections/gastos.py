"""
Sección Gastos del Dashboard P&G.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List

from components.metrics import render_metric_card
from components.charts import create_pie_chart
from utils.formatters import format_currency


def render_gastos(
    kpis: Dict[str, Dict[str, float]],
    aprovisionamientos: Dict[str, Dict[str, float]],
    personal: Dict[str, Dict[str, float]],
    otros_gastos: Dict[str, Dict[str, float]],
    years: List[str],
    year_selected: str
) -> None:
    """
    Renderiza la sección de Análisis de Gastos.

    Args:
        kpis: Diccionario de KPIs
        aprovisionamientos: Detalle de aprovisionamientos
        personal: Detalle de gastos de personal
        otros_gastos: Detalle de otros gastos
        years: Lista de años
        year_selected: Año principal de análisis
    """
    st.markdown("## Análisis de Gastos")

    # KPIs de gastos
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        aprov = kpis.get('aprovisionamientos', {}).get(year_selected, 0)
        render_metric_card("Aprovisionamientos", aprov)

    with col2:
        pers = kpis.get('gastos_personal', {}).get(year_selected, 0)
        render_metric_card("Gastos de Personal", pers)

    with col3:
        otros = kpis.get('otros_gastos', {}).get(year_selected, 0)
        render_metric_card("Otros Gastos Explotación", otros)

    with col4:
        amort = kpis.get('amortizacion', {}).get(year_selected, 0)
        render_metric_card("Amortización", amort)

    st.markdown("---")

    # Gráficos de gastos
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Evolución de Gastos Principales")

        data_gastos = pd.DataFrame({
            'Año': years,
            'Aprovisionamientos': [kpis.get('aprovisionamientos', {}).get(y, 0) for y in years],
            'Personal': [kpis.get('gastos_personal', {}).get(y, 0) for y in years],
            'Otros Gastos': [kpis.get('otros_gastos', {}).get(y, 0) for y in years],
            'Amortización': [kpis.get('amortizacion', {}).get(y, 0) for y in years]
        })

        fig = go.Figure()
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']

        for i, col in enumerate(['Aprovisionamientos', 'Personal', 'Otros Gastos', 'Amortización']):
            fig.add_trace(go.Scatter(
                x=data_gastos['Año'],
                y=data_gastos[col],
                name=col,
                mode='lines+markers',
                line=dict(width=3, color=colors[i]),
                marker=dict(size=10),
                fill='tonexty' if i > 0 else None
            ))

        fig.update_layout(height=400, yaxis_tickformat=',.0f', hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"### Detalle Aprovisionamientos ({year_selected})")

        if aprovisionamientos:
            aprov_filtered = {
                k: v[year_selected]
                for k, v in aprovisionamientos.items()
                if v.get(year_selected, 0) > 0
            }

            if aprov_filtered:
                fig = go.Figure(data=[go.Bar(
                    x=list(aprov_filtered.values()),
                    y=list(aprov_filtered.keys()),
                    orientation='h',
                    marker_color='#ff6b6b',
                    text=[format_currency(v) for v in aprov_filtered.values()],
                    textposition='outside'
                )])
                fig.update_layout(height=400, xaxis_tickformat=',.0f')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de aprovisionamientos para este año")
        else:
            st.info("No hay datos detallados de aprovisionamientos")

    # Segunda fila
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### Composición Gastos de Personal ({year_selected})")

        if personal:
            fig = create_pie_chart(
                labels=list(personal.keys()),
                values=[v.get(year_selected, 0) for v in personal.values()],
                height=350,
                hole=0.4,
                colors=['#4ecdc4', '#45b7d1', '#96ceb4']
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos detallados de personal")

    with col2:
        st.markdown(f"### Desglose Otros Gastos ({year_selected})")

        if otros_gastos:
            gastos_sorted = dict(sorted(
                otros_gastos.items(),
                key=lambda x: x[1].get(year_selected, 0),
                reverse=True
            ))

            fig = go.Figure(data=[go.Bar(
                x=list(gastos_sorted.keys()),
                y=[v.get(year_selected, 0) for v in gastos_sorted.values()],
                marker_color='#45b7d1',
                text=[format_currency(v.get(year_selected, 0)) for v in gastos_sorted.values()],
                textposition='outside'
            )])
            fig.update_layout(height=350, xaxis_tickangle=-45, yaxis_tickformat=',.0f')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos detallados de otros gastos")

    # Ratio gastos sobre ingresos
    st.markdown("---")
    st.markdown("### Ratio de Gastos sobre Ingresos")

    ratios = []
    for year in years:
        ing = kpis.get('ingresos', {}).get(year, 0)
        if ing > 0:
            ratios.append({
                'Año': year,
                'Aprovisionamientos': (kpis.get('aprovisionamientos', {}).get(year, 0) / ing) * 100,
                'Personal': (kpis.get('gastos_personal', {}).get(year, 0) / ing) * 100,
                'Otros Gastos': (kpis.get('otros_gastos', {}).get(year, 0) / ing) * 100,
                'Amortización': (kpis.get('amortizacion', {}).get(year, 0) / ing) * 100
            })

    if ratios:
        df_ratios = pd.DataFrame(ratios)

        fig = go.Figure()
        for col in ['Aprovisionamientos', 'Personal', 'Otros Gastos', 'Amortización']:
            fig.add_trace(go.Bar(name=col, x=df_ratios['Año'], y=df_ratios[col]))

        fig.update_layout(
            barmode='stack',
            height=400,
            yaxis_title='% sobre Ingresos',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)
