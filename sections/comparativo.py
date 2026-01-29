"""
Sección Análisis Comparativo del Dashboard P&G.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List

from components.charts import create_waterfall_chart
from utils.formatters import format_currency, calculate_variation


def render_comparativo(
    kpis: Dict[str, Dict[str, float]],
    years: List[str],
    year_selected: str,
    compare_year: str
) -> None:
    """
    Renderiza la sección de Análisis Comparativo.

    Args:
        kpis: Diccionario de KPIs
        years: Lista de años
        year_selected: Año principal de análisis
        compare_year: Año de comparación
    """
    st.markdown("## Análisis Comparativo")
    st.markdown(f"### Comparación {year_selected} vs {compare_year}")

    # Tabla comparativa
    comparativa = [
        {
            'Concepto': 'Ingresos Netos',
            year_selected: kpis.get('ingresos', {}).get(year_selected, 0),
            compare_year: kpis.get('ingresos', {}).get(compare_year, 0)
        },
        {
            'Concepto': 'Aprovisionamientos',
            year_selected: -kpis.get('aprovisionamientos', {}).get(year_selected, 0),
            compare_year: -kpis.get('aprovisionamientos', {}).get(compare_year, 0)
        },
        {
            'Concepto': 'Otros Ingresos',
            year_selected: kpis.get('otros_ingresos', {}).get(year_selected, 0),
            compare_year: kpis.get('otros_ingresos', {}).get(compare_year, 0)
        },
        {
            'Concepto': 'Gastos de Personal',
            year_selected: -kpis.get('gastos_personal', {}).get(year_selected, 0),
            compare_year: -kpis.get('gastos_personal', {}).get(compare_year, 0)
        },
        {
            'Concepto': 'Otros Gastos Explotación',
            year_selected: -kpis.get('otros_gastos', {}).get(year_selected, 0),
            compare_year: -kpis.get('otros_gastos', {}).get(compare_year, 0)
        },
        {
            'Concepto': 'Amortización',
            year_selected: -kpis.get('amortizacion', {}).get(year_selected, 0),
            compare_year: -kpis.get('amortizacion', {}).get(compare_year, 0)
        },
        {
            'Concepto': 'EBIT',
            year_selected: kpis.get('ebitda', {}).get(year_selected, 0),
            compare_year: kpis.get('ebitda', {}).get(compare_year, 0)
        },
        {
            'Concepto': 'Resultado Financiero',
            year_selected: kpis.get('resultado_financiero', {}).get(year_selected, 0),
            compare_year: kpis.get('resultado_financiero', {}).get(compare_year, 0)
        },
        {
            'Concepto': 'Resultado Neto',
            year_selected: kpis.get('resultado_neto', {}).get(year_selected, 0),
            compare_year: kpis.get('resultado_neto', {}).get(compare_year, 0)
        },
    ]

    df_comp = pd.DataFrame(comparativa)
    df_comp['Diferencia'] = df_comp[year_selected] - df_comp[compare_year]
    df_comp['Variación %'] = df_comp.apply(
        lambda row: calculate_variation(row[year_selected], row[compare_year]),
        axis=1
    )

    # Aplicar estilo con manejo de errores para matplotlib
    styled_df = df_comp.style.format({
        year_selected: '{:,.0f} €',
        compare_year: '{:,.0f} €',
        'Diferencia': '{:+,.0f} €',
        'Variación %': '{:+.1f}%'
    })
    try:
        styled_df = styled_df.background_gradient(subset=['Variación %'], cmap='RdYlGn')
    except Exception:
        pass  # Si matplotlib no está disponible, mostrar sin gradiente

    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Waterfall chart
    st.markdown(f"### Puente de Resultados: {compare_year} -> {year_selected}")

    resultado_anterior = kpis.get('resultado_neto', {}).get(compare_year, 0)
    resultado_actual = kpis.get('resultado_neto', {}).get(year_selected, 0)

    delta_ingresos = (
        kpis.get('ingresos', {}).get(year_selected, 0) -
        kpis.get('ingresos', {}).get(compare_year, 0)
    )
    delta_aprov = -(
        kpis.get('aprovisionamientos', {}).get(year_selected, 0) -
        kpis.get('aprovisionamientos', {}).get(compare_year, 0)
    )
    delta_personal = -(
        kpis.get('gastos_personal', {}).get(year_selected, 0) -
        kpis.get('gastos_personal', {}).get(compare_year, 0)
    )
    delta_otros = -(
        kpis.get('otros_gastos', {}).get(year_selected, 0) -
        kpis.get('otros_gastos', {}).get(compare_year, 0)
    )
    delta_amort = -(
        kpis.get('amortizacion', {}).get(year_selected, 0) -
        kpis.get('amortizacion', {}).get(compare_year, 0)
    )
    delta_financiero = (
        kpis.get('resultado_financiero', {}).get(year_selected, 0) -
        kpis.get('resultado_financiero', {}).get(compare_year, 0)
    )

    labels = [
        f"Resultado {compare_year}",
        "Ingresos",
        "Aprovision.",
        "Personal",
        "Otros Gastos",
        "Amortización",
        "Financiero",
        f"Resultado {year_selected}"
    ]

    values = [
        resultado_anterior,
        delta_ingresos,
        delta_aprov,
        delta_personal,
        delta_otros,
        delta_amort,
        delta_financiero,
        resultado_actual
    ]

    measures = [
        "absolute", "relative", "relative", "relative",
        "relative", "relative", "relative", "total"
    ]

    fig = create_waterfall_chart(labels, values, measures, height=500)
    st.plotly_chart(fig, use_container_width=True)
