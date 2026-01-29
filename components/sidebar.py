"""
Componente Sidebar para el Dashboard P&G y Balance.
"""

import streamlit as st
from typing import List, Tuple, Optional
from utils.export import (
    export_to_excel, export_to_pdf,
    is_excel_export_available, is_pdf_export_available
)


def render_sidebar(
    years: List[str],
    kpis: Optional[dict] = None,
    year_selected: Optional[str] = None,
    has_balance: bool = False
) -> Tuple[Optional[object], Optional[object], str, str, str]:
    """
    Renderiza el sidebar con controles de configuración.

    Args:
        years: Lista de años disponibles
        kpis: KPIs para exportación (opcional)
        year_selected: Año seleccionado para exportación
        has_balance: Si hay datos de balance cargados

    Returns:
        Tupla con (pyg_file, balance_file, year_selected, compare_year, section)
    """
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/bus.png", width=80)
        st.markdown("### 📁 Cargar Datos")

        # Archivo P&G
        pyg_file = st.file_uploader(
            "📊 Pérdidas y Ganancias",
            type=['xlsx', 'xls'],
            help="Archivo Excel con el formato de Pérdidas y Ganancias",
            key="file_uploader_pyg"
        )

        if pyg_file:
            st.success("✅ P&G cargado")

        # Archivo Balance
        balance_file = st.file_uploader(
            "📋 Balance de Situación",
            type=['xlsx', 'xls'],
            help="Archivo Excel con el Balance de Situación (opcional)",
            key="file_uploader_balance"
        )

        if balance_file:
            st.success("✅ Balance cargado")

        st.markdown("---")
        st.markdown("### ⚙️ Configuración")

        year_selected = st.selectbox(
            "Año de análisis principal",
            years,
            index=0,
            key="year_selected_pyg"
        )

        # Años para comparación (excluir el seleccionado como primera opción)
        compare_options = [y for y in years if y != year_selected] + [year_selected]
        compare_year = st.selectbox(
            "Año de comparación",
            compare_options,
            index=0,
            key="compare_year_pyg"
        )

        st.markdown("---")
        st.markdown("### 📈 Navegación")

        # Secciones disponibles según datos cargados
        sections = [
            "🏠 Resumen Ejecutivo",
            "💰 Ingresos",
            "📉 Gastos",
            "📊 Análisis Comparativo",
            "🎯 KPIs Avanzados"
        ]

        # Añadir secciones de Balance si está cargado
        if has_balance:
            sections.extend([
                "📋 Balance de Situación",
                "📐 Ratios Financieros"
            ])

        section = st.radio(
            "Ir a sección:",
            sections,
            key="section_pyg"
        )

        # Sección de exportación
        if kpis is not None:
            st.markdown("---")
            st.markdown("### 💾 Exportar")

            col1, col2 = st.columns(2)

            with col1:
                if is_excel_export_available():
                    excel_data = export_to_excel(
                        kpis, years,
                        company_name="AUTOPULLMAN SAN SEBASTIÁN S.L."
                    )
                    if excel_data:
                        st.download_button(
                            label="📥 Excel",
                            data=excel_data,
                            file_name=f"dashboard_pyg_{year_selected}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="download_excel_pyg"
                        )
                else:
                    st.caption("Excel no disponible")

            with col2:
                if is_pdf_export_available():
                    pdf_data = export_to_pdf(
                        kpis, years, year_selected,
                        company_name="AUTOPULLMAN SAN SEBASTIÁN S.L."
                    )
                    if pdf_data:
                        st.download_button(
                            label="📥 PDF",
                            data=pdf_data,
                            file_name=f"resumen_pyg_{year_selected}.pdf",
                            mime="application/pdf",
                            key="download_pdf_pyg"
                        )
                else:
                    st.caption("PDF no disponible")

    return pyg_file, balance_file, year_selected, compare_year, section
