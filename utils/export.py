"""
Módulo de exportación para el Dashboard P&G.
Genera reportes en Excel y PDF.
"""

import io
from typing import Dict, Any, List, Optional
from datetime import datetime

import pandas as pd

try:
    import xlsxwriter
    XLSXWRITER_AVAILABLE = True
except ImportError:
    XLSXWRITER_AVAILABLE = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from .formatters import format_currency, format_percentage


def export_to_excel(
    kpis: Dict[str, Dict[str, float]],
    years: List[str],
    company_name: str = "Empresa",
    detailed_data: Optional[Dict] = None
) -> Optional[bytes]:
    """
    Exporta los datos a un archivo Excel.

    Args:
        kpis: Diccionario de KPIs
        years: Lista de años
        company_name: Nombre de la empresa
        detailed_data: Datos detallados opcionales

    Returns:
        Bytes del archivo Excel o None si xlsxwriter no está disponible
    """
    if not XLSXWRITER_AVAILABLE:
        return None

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})

    # Formatos
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#1f77b4',
        'font_color': 'white',
        'align': 'center',
        'border': 1
    })
    currency_format = workbook.add_format({
        'num_format': '#,##0 "EUR"',
        'align': 'right',
        'border': 1
    })
    percent_format = workbook.add_format({
        'num_format': '0.0%',
        'align': 'right',
        'border': 1
    })
    text_format = workbook.add_format({
        'align': 'left',
        'border': 1
    })
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'left'
    })

    # Hoja de Resumen
    ws_resumen = workbook.add_worksheet('Resumen Ejecutivo')
    ws_resumen.set_column('A:A', 30)
    ws_resumen.set_column('B:E', 15)

    ws_resumen.write('A1', f'Dashboard P&G - {company_name}', title_format)
    ws_resumen.write('A2', f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}')

    row = 4
    ws_resumen.write(row, 0, 'Concepto', header_format)
    for i, year in enumerate(years):
        ws_resumen.write(row, i + 1, year, header_format)

    kpi_labels = {
        'ingresos': 'Ingresos Netos',
        'aprovisionamientos': 'Aprovisionamientos',
        'gastos_personal': 'Gastos de Personal',
        'otros_gastos': 'Otros Gastos',
        'amortizacion': 'Amortización',
        'ebitda': 'EBIT (Resultado Explotación)',
        'resultado_financiero': 'Resultado Financiero',
        'resultado_neto': 'Resultado Neto',
    }

    row += 1
    for kpi_key, label in kpi_labels.items():
        if kpi_key in kpis:
            ws_resumen.write(row, 0, label, text_format)
            for i, year in enumerate(years):
                value = kpis[kpi_key].get(year, 0)
                ws_resumen.write(row, i + 1, value, currency_format)
            row += 1

    # Hoja de Márgenes
    ws_margenes = workbook.add_worksheet('Márgenes')
    ws_margenes.set_column('A:A', 25)
    ws_margenes.set_column('B:E', 12)

    ws_margenes.write('A1', 'Análisis de Márgenes', title_format)

    row = 3
    ws_margenes.write(row, 0, 'Indicador', header_format)
    for i, year in enumerate(years):
        ws_margenes.write(row, i + 1, year, header_format)

    row += 1
    for year_idx, year in enumerate(years):
        ingresos = kpis.get('ingresos', {}).get(year, 0)
        ebit = kpis.get('ebitda', {}).get(year, 0)
        neto = kpis.get('resultado_neto', {}).get(year, 0)
        aprov = kpis.get('aprovisionamientos', {}).get(year, 0)
        amort = kpis.get('amortizacion', {}).get(year, 0)

        if year_idx == 0:
            margenes = [
                ('Margen Bruto', (ingresos - aprov) / ingresos if ingresos else 0),
                ('Margen EBITDA', (ebit + amort) / ingresos if ingresos else 0),
                ('Margen EBIT', ebit / ingresos if ingresos else 0),
                ('Margen Neto', neto / ingresos if ingresos else 0),
            ]
            for margin_name, _ in margenes:
                ws_margenes.write(row, 0, margin_name, text_format)
                row += 1
            row = 4

        col = year_idx + 1
        row_temp = row
        for margin_name, margin_val in [
            ('Margen Bruto', (ingresos - aprov) / ingresos if ingresos else 0),
            ('Margen EBITDA', (ebit + amort) / ingresos if ingresos else 0),
            ('Margen EBIT', ebit / ingresos if ingresos else 0),
            ('Margen Neto', neto / ingresos if ingresos else 0),
        ]:
            ws_margenes.write(row_temp, col, margin_val, percent_format)
            row_temp += 1

    workbook.close()
    output.seek(0)
    return output.getvalue()


def export_to_pdf(
    kpis: Dict[str, Dict[str, float]],
    years: List[str],
    year_selected: str,
    company_name: str = "Empresa"
) -> Optional[bytes]:
    """
    Exporta un resumen ejecutivo a PDF.

    Args:
        kpis: Diccionario de KPIs
        years: Lista de años
        year_selected: Año principal de análisis
        company_name: Nombre de la empresa

    Returns:
        Bytes del archivo PDF o None si reportlab no está disponible
    """
    if not REPORTLAB_AVAILABLE:
        return None

    output = io.BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20
    )
    normal_style = styles['Normal']

    elements = []

    # Título
    elements.append(Paragraph(f"Dashboard P&G - {company_name}", title_style))
    elements.append(Paragraph(
        f"Resumen Ejecutivo - Año {year_selected}",
        subtitle_style
    ))
    elements.append(Paragraph(
        f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        normal_style
    ))
    elements.append(Spacer(1, 20))

    # Tabla de KPIs principales
    elements.append(Paragraph("KPIs Principales", subtitle_style))

    ingresos = kpis.get('ingresos', {}).get(year_selected, 0)
    ebit = kpis.get('ebitda', {}).get(year_selected, 0)
    neto = kpis.get('resultado_neto', {}).get(year_selected, 0)

    data = [
        ['Indicador', 'Valor', 'Margen'],
        ['Ingresos Netos', format_currency(ingresos), '-'],
        ['EBIT', format_currency(ebit),
         format_percentage(ebit / ingresos * 100 if ingresos else 0)],
        ['Resultado Neto', format_currency(neto),
         format_percentage(neto / ingresos * 100 if ingresos else 0)],
    ]

    table = Table(data, colWidths=[6*cm, 5*cm, 4*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 30))

    # Tabla de Gastos
    elements.append(Paragraph("Estructura de Costes", subtitle_style))

    aprov = kpis.get('aprovisionamientos', {}).get(year_selected, 0)
    personal = kpis.get('gastos_personal', {}).get(year_selected, 0)
    otros = kpis.get('otros_gastos', {}).get(year_selected, 0)
    amort = kpis.get('amortizacion', {}).get(year_selected, 0)
    total_gastos = aprov + personal + otros + amort

    data_gastos = [
        ['Concepto', 'Importe', '% s/Total'],
        ['Aprovisionamientos', format_currency(aprov),
         format_percentage(aprov / total_gastos * 100 if total_gastos else 0)],
        ['Gastos de Personal', format_currency(personal),
         format_percentage(personal / total_gastos * 100 if total_gastos else 0)],
        ['Otros Gastos', format_currency(otros),
         format_percentage(otros / total_gastos * 100 if total_gastos else 0)],
        ['Amortización', format_currency(amort),
         format_percentage(amort / total_gastos * 100 if total_gastos else 0)],
        ['TOTAL', format_currency(total_gastos), '100%'],
    ]

    table_gastos = Table(data_gastos, colWidths=[6*cm, 5*cm, 4*cm])
    table_gastos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8e8e8')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(table_gastos)

    doc.build(elements)
    output.seek(0)
    return output.getvalue()


def is_excel_export_available() -> bool:
    """Verifica si la exportación a Excel está disponible."""
    return XLSXWRITER_AVAILABLE


def is_pdf_export_available() -> bool:
    """Verifica si la exportación a PDF está disponible."""
    return REPORTLAB_AVAILABLE
