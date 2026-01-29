"""
Sección Ingresos del Dashboard P&G.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List

from components.metrics import render_metric_card
from components.charts import create_pie_chart
from utils.formatters import format_currency, calculate_variation


def render_ingresos(
    kpis: Dict[str, Dict[str, float]],
    servicios: Dict[str, Dict[str, float]],
    years: List[str],
    year_selected: str
) -> None:
    """
    Renderiza la sección de Análisis de Ingresos.

    Args:
        kpis: Diccionario de KPIs
        servicios: Diccionario de ingresos por servicio
        years: Lista de años
        year_selected: Año principal de análisis
    """
    st.markdown("## Análisis de Ingresos")

    # KPIs de ingresos
    col1, col2, col3 = st.columns(3)

    ing_actual = kpis.get('ingresos', {}).get(year_selected, 0)
    otros_ing = kpis.get('otros_ingresos', {}).get(year_selected, 0)
    total = ing_actual + otros_ing

    with col1:
        render_metric_card("Ingresos Totales", ing_actual)

    with col2:
        render_metric_card("Otros Ingresos", otros_ing)

    with col3:
        render_metric_card("Total Ingresos Operativos", total)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### Ingresos por Tipo de Servicio ({year_selected})")

        if servicios:
            servicios_filtered = {
                k: v[year_selected]
                for k, v in servicios.items()
                if v.get(year_selected, 0) > 0
            }

            if servicios_filtered:
                fig = create_pie_chart(
                    labels=list(servicios_filtered.keys()),
                    values=list(servicios_filtered.values()),
                    height=450,
                    hole=0.3
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay servicios con valores positivos para este año")
        else:
            st.info("No hay datos detallados de servicios disponibles")

    with col2:
        st.markdown("### Evolución de Ingresos por Servicio")

        if servicios:
            data_servicios = []
            for nombre, valores in servicios.items():
                for year in years:
                    if valores.get(year, 0) > 0:
                        nombre_corto = nombre[:30] + '...' if len(nombre) > 30 else nombre
                        data_servicios.append({
                            'Servicio': nombre_corto,
                            'Año': year,
                            'Importe': valores.get(year, 0)
                        })

            if data_servicios:
                df_serv = pd.DataFrame(data_servicios)

                fig = px.bar(
                    df_serv,
                    x='Año',
                    y='Importe',
                    color='Servicio',
                    barmode='stack',
                    height=450
                )
                fig.update_layout(yaxis_tickformat=',.0f')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de evolución disponibles")
        else:
            st.info("No hay datos detallados de servicios disponibles")

    # Tabla detallada
    st.markdown("### Detalle de Ingresos por Servicio")

    if servicios:
        tabla_servicios = []
        for nombre, valores in servicios.items():
            fila = {'Servicio': nombre}
            for year in years:
                fila[year] = valores.get(year, 0)
            fila['Var 24-25'] = calculate_variation(
                valores.get('2025', 0),
                valores.get('2024', 0)
            )
            tabla_servicios.append(fila)

        df_tabla = pd.DataFrame(tabla_servicios)

        # Filtrar servicios con valores
        year_cols = [y for y in years if y in df_tabla.columns]
        if year_cols:
            df_tabla = df_tabla[df_tabla[year_cols].sum(axis=1) > 0]
            df_tabla = df_tabla.sort_values(years[0], ascending=False)

            # Formatear
            format_dict = {y: '{:,.0f} €' for y in years}
            format_dict['Var 24-25'] = '{:+.1f}%'

            styled_tabla = df_tabla.style.format(format_dict)
            try:
                styled_tabla = styled_tabla.background_gradient(subset=['Var 24-25'], cmap='RdYlGn')
            except Exception:
                pass  # Si matplotlib no está disponible, mostrar sin gradiente

            st.dataframe(styled_tabla, use_container_width=True, hide_index=True)
    else:
        st.info("No hay datos detallados de servicios disponibles")
