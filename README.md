# Dashboard P&G - Autopullman San Sebastián

Dashboard financiero interactivo para análisis de Pérdidas y Ganancias (P&G).

## Descripción

Aplicación web desarrollada con Streamlit que permite visualizar y analizar datos financieros de P&G de forma interactiva. Incluye:

- **Resumen Ejecutivo**: KPIs principales, evolución de resultados y distribución de costes
- **Análisis de Ingresos**: Desglose por tipo de servicio y evolución temporal
- **Análisis de Gastos**: Estructura de costes y ratios sobre ingresos
- **Análisis Comparativo**: Comparación entre años con gráfico waterfall
- **KPIs Avanzados**: Márgenes, ratios y gráfico radar comparativo

## Requisitos

- Python 3.9+
- Dependencias listadas en `requirements.txt`

## Instalación

```bash
# Clonar o descargar el proyecto
cd dashboard-pyg

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`

## Formato del Archivo Excel

El archivo Excel debe seguir el formato estándar de P&G con:

### Columnas requeridas:
- **Concepto**: Descripción de cada línea del P&G
- **Años**: Columnas con los años a analizar (ej: 2022, 2023, 2024, 2025)

### Conceptos reconocidos:

| Concepto | Descripción |
|----------|-------------|
| 1. Importe neto de la cifra de negocios | Ingresos principales |
| 4. Aprovisionamientos | Costes de aprovisionamiento |
| 5. Otros ingresos de explotación | Ingresos secundarios |
| 6. Gastos de personal | Sueldos, SS, etc. |
| 7. Otros gastos de explotación | Gastos operativos |
| 8. Amortización del inmovilizado | Depreciación |
| A) Resultado de explotación | EBIT |
| B) Resultado financiero | Ingresos - Gastos financieros |
| D. Resultado del ejercicio | Beneficio neto |

### Códigos para datos detallados (opcional):

- `705.0.0.XXX`: Tipos de servicios
- `602.0.0.XXX`: Detalle aprovisionamientos
- `640 SUELDOS`: Sueldos y salarios
- `642 SEGURIDAD SOCIAL`: Cotizaciones
- `622 REPARACIONES`: Mantenimiento
- `625 PRIMAS DE SEGUROS`: Seguros

## Estructura del Proyecto

```
dashboard-pyg/
├── app.py                 # Punto de entrada principal
├── requirements.txt       # Dependencias
├── README.md              # Este archivo
├── config/
│   ├── __init__.py
│   └── kpi_mappings.py    # Configuración de KPIs
├── utils/
│   ├── __init__.py
│   ├── data_loader.py     # Carga de datos
│   ├── kpi_extractor.py   # Extracción de KPIs
│   ├── formatters.py      # Funciones de formateo
│   └── export.py          # Exportación PDF/Excel
├── components/
│   ├── __init__.py
│   ├── sidebar.py         # Barra lateral
│   ├── metrics.py         # Tarjetas de métricas
│   └── charts.py          # Gráficos
└── sections/
    ├── __init__.py
    ├── resumen.py         # Resumen Ejecutivo
    ├── ingresos.py        # Análisis de Ingresos
    ├── gastos.py          # Análisis de Gastos
    ├── comparativo.py     # Análisis Comparativo
    └── kpis_avanzados.py  # KPIs Avanzados
```

## Exportación

El dashboard permite exportar los datos en dos formatos:

- **Excel**: Resumen completo con KPIs y márgenes
- **PDF**: Resumen ejecutivo con tablas principales

Los botones de exportación aparecen en la barra lateral una vez cargado un archivo.

## Personalización

### Añadir nuevos KPIs

Edita `config/kpi_mappings.py` y añade nuevos patrones:

```python
KPI_MAPPINGS = {
    'mi_nuevo_kpi': {
        'patterns': [
            r'patrón_regex_1',
            r'patrón_regex_2',
        ],
        'sign': 1,  # 1 positivo, -1 para invertir
        'required': False,
        'default': 0,
    },
}
```

### Cambiar años por defecto

Modifica `YEARS` en `config/kpi_mappings.py`:

```python
YEARS = ['2023', '2024', '2025', '2026']
```

## Manejo de Errores

La aplicación maneja los siguientes errores:

- **Archivo inválido**: Se muestra mensaje si el Excel no es válido
- **Formato incorrecto**: Se indica qué columnas faltan
- **KPIs no encontrados**: Se muestra advertencia y se usan valores por defecto

## Tecnologías

- [Streamlit](https://streamlit.io/) - Framework web
- [Plotly](https://plotly.com/) - Visualizaciones interactivas
- [Pandas](https://pandas.pydata.org/) - Procesamiento de datos
- [XlsxWriter](https://xlsxwriter.readthedocs.io/) - Exportación Excel
- [ReportLab](https://www.reportlab.com/) - Generación PDF
