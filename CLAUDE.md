# Dashboard Financiero P&G y Balance

## Descripción
Dashboard interactivo en Streamlit para análisis de Pérdidas y Ganancias y Balance de Situación de AUTOPULLMAN SAN SEBASTIÁN S.L.

## Último Cambio Realizado
- Migrado a Python 3.12 con virtual environment (`venv/`) para evitar crashes de Python 3.14 en macOS
- Corregidos errores de `background_gradient requires matplotlib` en secciones Comparativo, KPIs Avanzados e Ingresos
- Mejorados patrones de búsqueda de KPIs para detectar "RESULTADO DE EXPLOTACION" (sin acento) y "RESULTADO DEL EJERCICIO"

## Estado Actual

### Funciona:
- Carga de archivo P&G Excel
- Carga de archivo Balance Excel (opcional)
- Extracción de todos los KPIs (ingresos, ebitda, resultado_neto, etc.)
- Sección Resumen Ejecutivo
- Sección Ingresos
- Sección Gastos
- Sección Análisis Comparativo
- Sección KPIs Avanzados
- Sección Balance de Situación
- Sección Ratios Financieros

### Requisitos:
- Python 3.12 (usar virtual environment)
- Dependencias: streamlit, pandas, plotly, openpyxl, matplotlib

## Cómo Ejecutar
```bash
source venv/bin/activate
streamlit run app.py
```

## Próximo Paso Concreto
- Verificar estabilidad del dashboard con Python 3.12
- Considerar agregar tests automatizados para los extractores de KPIs
- Opcional: Mejorar UI/UX y agregar más gráficos comparativos

## Estructura del Proyecto
```
dashboard-pyg/
├── app.py                 # Entrada principal Streamlit
├── config/
│   └── kpi_mappings.py    # Patrones regex para KPIs
├── components/
│   ├── sidebar.py         # Barra lateral
│   └── charts.py          # Funciones de gráficos
├── sections/
│   ├── __init__.py
│   ├── resumen.py
│   ├── ingresos.py
│   ├── gastos.py
│   ├── comparativo.py
│   ├── kpis_avanzados.py
│   └── balance.py
├── utils/
│   ├── data_loader.py     # Carga P&G Excel
│   ├── kpi_extractor.py   # Extracción de KPIs
│   ├── balance_loader.py  # Carga Balance Excel
│   ├── formatters.py
│   └── export.py
└── venv/                  # Virtual environment Python 3.12
```
