"""
Configuración flexible de mapeo de KPIs para el Dashboard P&G.

Cada KPI se define con:
- patterns: Lista de patrones regex para buscar el concepto
- sign: 1 para valores positivos, -1 para invertir signo (gastos)
- required: Si es obligatorio encontrar este KPI
- default: Valor por defecto si no se encuentra (solo para no requeridos)
"""

import re

YEARS = ['2022', '2023', '2024', '2025']

KPI_MAPPINGS = {
    'ingresos': {
        'patterns': [
            r'1\.?\s*importe\s+neto\s+de\s+la\s+cifra\s+de\s+negocios',
            r'importe\s+neto\s+cifra\s+negocios',
            r'cifra\s+de\s+negocios',
            r'ventas\s+netas',
            r'ingresos\s+netos',
        ],
        'sign': 1,
        'required': True,
    },
    'aprovisionamientos': {
        'patterns': [
            r'4\.?\s*aprovisionamientos',
            r'aprovisionamientos',
            r'compras\s+de\s+mercader[ií]as',
        ],
        'sign': -1,  # Los gastos se muestran en positivo
        'required': True,
    },
    'gastos_personal': {
        'patterns': [
            r'6\.?\s*gastos\s+de\s+personal',
            r'gastos\s+personal',
            r'gastos\s+de\s+personal',
        ],
        'sign': -1,
        'required': True,
    },
    'otros_gastos': {
        'patterns': [
            r'7\.?\s*otros\s+gastos\s+de\s+explotaci[oó]n',
            r'otros\s+gastos\s+explotaci[oó]n',
            r'otros\s+gastos\s+de\s+explotaci[oó]n',
        ],
        'sign': -1,
        'required': True,
    },
    'amortizacion': {
        'patterns': [
            r'8\.?\s*amortizaci[oó]n\s+del\s+inmovilizado',
            r'amortizaci[oó]n\s+inmovilizado',
            r'amortizaci[oó]n',
        ],
        'sign': -1,
        'required': True,
    },
    'ebitda': {
        'patterns': [
            r'a\)?\s*resultado\s+de\s+explotacion',  # Sin acento
            r'a\)?\s*resultado\s+de\s+explotaci[oó]n',
            r'\d+\.?\s*resultado\s+de\s+explotaci[oó]n',
            r'resultado\s+de\s+explotacion',  # Sin acento
            r'resultado\s+de\s+explotaci[oó]n',
            r'resultado\s+explotaci[oó]n',
            r'ebitda',
            r'ebit\b',
            r'beneficio\s+operativo',
        ],
        'sign': 1,
        'required': True,
    },
    'resultado_financiero': {
        'patterns': [
            r'b\)?\s*resultado\s+financiero',
            r'resultado\s+financiero',
        ],
        'sign': 1,
        'required': False,
        'default': 0,
    },
    'resultado_neto': {
        'patterns': [
            r'd\)?\s*resultado\s+del\s+ejercicio',
            r'\d+\.?\s*resultado\s+del\s+ejercicio',
            r'resultado\s+del\s+ejercicio',
            r'beneficio\s+neto',
            r'resultado\s+neto',
            r'beneficio\s*/\s*p[eé]rdida\s+del\s+ejercicio',
            r'resultado\s+despu[eé]s\s+de\s+impuestos',
        ],
        'sign': 1,
        'required': True,
    },
    'otros_ingresos': {
        'patterns': [
            r'5\.?\s*otros\s+ingresos\s+de\s+explotaci[oó]n',
            r'otros\s+ingresos\s+explotaci[oó]n',
            r'otros\s+ingresos',
        ],
        'sign': 1,
        'required': False,
        'default': 0,
    },
    'gastos_financieros': {
        'patterns': [
            r'14\.?\s*gastos\s+financieros',
            r'gastos\s+financieros',
        ],
        'sign': -1,
        'required': False,
        'default': 0,
    },
}

# Mapeos para datos detallados
DETAILED_MAPPINGS = {
    'servicios': {
        'parent_pattern': r'705\s+PRESTACIONES\s+DE\s+SERVICIOS',
        'item_pattern': r'^705\.0\.0\.',
        'stop_pattern': r'2\.\s*Variaci[oó]n',
    },
    'aprovisionamientos_detalle': {
        'item_pattern': r'^602\.0\.0\.',
    },
    'personal_detalle': {
        'categories': [
            (r'640\s+SUELDOS', 'Sueldos y Salarios'),
            (r'642\s+SEGURIDAD\s+SOCIAL', 'Seguridad Social'),
            (r'641\s+INDEMNIZACIONES', 'Indemnizaciones'),
        ],
    },
    'otros_gastos_detalle': {
        'categories': [
            (r'622\s+REPARACIONES', 'Reparaciones y Mantenimiento'),
            (r'623\s+SERVICIOS\s+DE\s+PROFESIONALES', 'Servicios Profesionales'),
            (r'625\s+PRIMAS\s+DE\s+SEGUROS', 'Seguros'),
            (r'627\s+PUBLICIDAD', 'Publicidad y Marketing'),
            (r'628\s+SUMINISTROS', 'Suministros'),
            (r'629\s+OTROS\s+SERVICIOS', 'Otros Servicios'),
            (r'631\s+OTROS\s+TRIBUTOS', 'Tributos'),
        ],
    },
}


def match_pattern(text: str, patterns: list) -> bool:
    """Verifica si el texto coincide con alguno de los patrones."""
    text_lower = text.lower().strip()
    for pattern in patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False
