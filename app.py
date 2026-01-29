"""
Dashboard Financiero P&G y Balance - Autopullman San Sebastián S.L.

Aplicación Streamlit para análisis de Pérdidas y Ganancias y Balance de Situación.
"""

import streamlit as st
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar módulos locales
from config.kpi_mappings import YEARS
from utils.data_loader import DataLoader, DataLoadError, ValidationError
from utils.kpi_extractor import KPIExtractor
from utils.balance_loader import BalanceLoader, BalanceKPIExtractor, calculate_financial_ratios
from components.sidebar import render_sidebar
from sections import (
    render_resumen,
    render_ingresos,
    render_gastos,
    render_comparativo,
    render_kpis_avanzados
)
from sections.balance import render_balance, render_ratios_financieros

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Financiero - Autopullman San Sebastián",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    .highlight-positive {
        color: #28a745;
    }
    .highlight-negative {
        color: #dc3545;
    }
    .error-box {
        background-color: #fee2e2;
        border: 1px solid #fca5a5;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fef3c7;
        border: 1px solid #fcd34d;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #dbeafe;
        border: 1px solid #93c5fd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def show_welcome_screen():
    """Muestra la pantalla de bienvenida cuando no hay archivo cargado."""
    st.info("👆 Por favor, sube al menos el archivo de **Pérdidas y Ganancias** en la barra lateral para comenzar el análisis.")

    st.markdown("---")
    st.markdown("### 🎯 ¿Qué incluye este dashboard?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **📊 Pérdidas y Ganancias**
        - Ingresos por servicio
        - Análisis de gastos
        - Márgenes de beneficio
        - Evolución temporal
        """)

    with col2:
        st.markdown("""
        **📋 Balance de Situación**
        - Estructura del Activo
        - Patrimonio y Pasivo
        - Fondo de Maniobra
        - Evolución patrimonial
        """)

    with col3:
        st.markdown("""
        **📐 Ratios Financieros**
        - ROE, ROA
        - Liquidez y Solvencia
        - Endeudamiento
        - Análisis integral
        """)

    st.markdown("---")
    st.markdown("""
    <div class="info-box">
        <strong>💡 Tip:</strong> Sube ambos archivos (P&G y Balance) para obtener un análisis financiero completo
        con ratios avanzados como ROE, ROA, Liquidez y Endeudamiento.
    </div>
    """, unsafe_allow_html=True)


def show_error(title: str, message: str, details: str = None):
    """Muestra un mensaje de error formateado."""
    st.markdown(f"""
    <div class="error-box">
        <strong>❌ {title}</strong><br>
        {message}
    </div>
    """, unsafe_allow_html=True)

    if details:
        with st.expander("Ver detalles técnicos"):
            st.code(details)


def show_warning(message: str):
    """Muestra un mensaje de advertencia."""
    st.markdown(f"""
    <div class="warning-box">
        <strong>⚠️ Advertencia:</strong> {message}
    </div>
    """, unsafe_allow_html=True)


def main():
    """Función principal de la aplicación."""

    # Header
    st.markdown('<h1 class="main-header">📊 Dashboard Financiero</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Análisis de P&G y Balance - AUTOPULLMAN SAN SEBASTIÁN S.L.</p>', unsafe_allow_html=True)

    # Inicializar variables
    years = YEARS
    kpis = None
    balance_kpis = None
    servicios = None
    aprovisionamientos = None
    personal = None
    otros_gastos = None
    activo_detalle = None
    pasivo_detalle = None
    ratios = None

    # Detectar si hay balance en session_state para mostrar secciones correctas
    has_balance = st.session_state.get('has_balance', False)

    # Renderizar sidebar UNA SOLA VEZ
    pyg_file, balance_file, year_selected, compare_year, section = render_sidebar(YEARS, has_balance=has_balance)

    # Actualizar has_balance basado en si hay archivo
    if balance_file is not None:
        st.session_state['has_balance'] = True
        has_balance = True
    else:
        st.session_state['has_balance'] = False
        has_balance = False

    # Si no hay archivo P&G, mostrar pantalla de bienvenida
    if pyg_file is None:
        show_welcome_screen()
        return

    # ===== CARGAR P&G =====
    try:
        loader = DataLoader()
        df_pyg = loader.load(pyg_file)
        years = loader.get_years()

    except DataLoadError as e:
        show_error(
            "Error al cargar P&G",
            str(e),
            "Verifica que el archivo es un Excel válido con extensión .xlsx o .xls"
        )
        return

    except ValidationError as e:
        show_error(
            "Error de validación en P&G",
            str(e),
            "El archivo debe contener columnas con años (ej: 2022, 2023, 2024, 2025) y una columna de conceptos."
        )
        return

    except Exception as e:
        logger.exception("Error inesperado al cargar P&G")
        show_error(
            "Error inesperado",
            "Ocurrió un error al procesar el archivo de P&G.",
            str(e)
        )
        return

    # Extraer KPIs de P&G
    try:
        extractor = KPIExtractor(df_pyg, years)
        kpis = extractor.extract_all()
        servicios, aprovisionamientos, personal, otros_gastos = extractor.extract_detailed_data()

        # Mostrar advertencia si faltan KPIs
        missing = extractor.get_missing_kpis()
        if missing:
            show_warning(
                f"No se encontraron algunos KPIs en P&G: {', '.join(missing)}. "
                "Los valores se mostrarán como 0."
            )

    except Exception as e:
        logger.exception("Error al extraer KPIs de P&G")
        show_error(
            "Error al analizar P&G",
            "No se pudieron extraer los indicadores del archivo.",
            str(e)
        )
        return

    # ===== CARGAR BALANCE (opcional) =====
    if balance_file is not None:
        try:
            balance_loader = BalanceLoader()
            df_balance = balance_loader.load(balance_file)

            balance_extractor = BalanceKPIExtractor(df_balance, years)
            balance_kpis = balance_extractor.extract_all()
            activo_detalle = balance_extractor.extract_detailed_activo()
            pasivo_detalle = balance_extractor.extract_detailed_pasivo()

            # Calcular ratios financieros
            ratios = calculate_financial_ratios(balance_kpis, kpis, years)

            has_balance = True
            st.session_state['has_balance'] = True

            st.markdown("""
            <div class="info-box">
                <strong>✅ Análisis completo disponible:</strong> Se han cargado P&G y Balance.
                Recarga la página para ver las secciones de Balance y Ratios Financieros en el menú lateral.
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            logger.exception("Error al cargar Balance")
            show_warning(
                f"No se pudo cargar el Balance: {str(e)}. "
                "El análisis continuará solo con los datos de P&G."
            )

    # Renderizar sección seleccionada
    try:
        if "Resumen" in section:
            render_resumen(kpis, years, year_selected, compare_year)

        elif "Ingresos" in section:
            render_ingresos(kpis, servicios, years, year_selected)

        elif "Gastos" in section:
            render_gastos(kpis, aprovisionamientos, personal, otros_gastos, years, year_selected)

        elif "Comparativo" in section:
            render_comparativo(kpis, years, year_selected, compare_year)

        elif "KPIs Avanzados" in section:
            render_kpis_avanzados(kpis, years, year_selected, compare_year)

        elif "Balance" in section:
            if has_balance:
                render_balance(balance_kpis, activo_detalle, pasivo_detalle, years, year_selected, compare_year)
            else:
                st.warning("⚠️ Para ver el Balance de Situación, sube el archivo correspondiente en la barra lateral.")

        elif "Ratios" in section:
            if has_balance and ratios:
                render_ratios_financieros(ratios, years, year_selected, compare_year)
            else:
                st.warning("⚠️ Para ver los Ratios Financieros, sube el archivo de Balance de Situación en la barra lateral.")

    except Exception as e:
        logger.exception(f"Error al renderizar sección: {section}")
        show_error(
            "Error al mostrar sección",
            f"Ocurrió un error al renderizar la sección '{section}'.",
            str(e)
        )

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #888; font-size: 0.9rem;'>
            📊 Dashboard Financiero P&G y Balance | Desarrollado con Streamlit y Plotly
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
