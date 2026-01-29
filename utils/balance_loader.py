"""
Cargador y procesador de datos del Balance de Situación.
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional


class BalanceLoader:
    """Carga y procesa archivos Excel de Balance de Situación."""

    def __init__(self):
        self.df = None
        self.years = []

    def load(self, uploaded_file) -> pd.DataFrame:
        """Carga el archivo Excel del Balance."""
        self.df = pd.read_excel(uploaded_file, sheet_name=0)

        # Renombrar columnas
        self.df.columns = ['Col1', 'Col2', 'Concepto', 'Col4', 'Col5', 'Col6', '2025', '2024', '2023', '2022']

        # Detectar años disponibles
        self.years = ['2025', '2024', '2023', '2022']

        # Convertir valores a numérico
        for year in self.years:
            self.df[year] = pd.to_numeric(self.df[year], errors='coerce').fillna(0)

        return self.df

    def get_years(self) -> List[str]:
        """Retorna los años disponibles."""
        return self.years


class BalanceKPIExtractor:
    """Extrae KPIs del Balance de Situación."""

    def __init__(self, df: pd.DataFrame, years: List[str]):
        self.df = df
        self.years = years

    def extract_all(self) -> Dict:
        """Extrae todos los KPIs del Balance."""
        kpis = {}

        # Buscar valores clave
        for idx, row in self.df.iterrows():
            # Combinar columnas de texto para buscar
            concepto = ''
            for col in ['Col1', 'Col2', 'Concepto']:
                if col in self.df.columns and pd.notna(row.get(col)):
                    concepto += ' ' + str(row.get(col, ''))
            concepto = concepto.lower().strip()

            # ACTIVO
            if 'a) activo no corriente' in concepto:
                kpis['activo_no_corriente'] = {year: row[year] for year in self.years}
            elif 'b) activo corriente' in concepto:
                kpis['activo_corriente'] = {year: row[year] for year in self.years}
            elif 'total activo (a+b)' in concepto:
                kpis['total_activo'] = {year: row[year] for year in self.years}
            elif 'i. existencias' in concepto and 'activo' not in concepto:
                kpis['existencias'] = {year: row[year] for year in self.years}
            elif 'ii. deudores comerciales y otras cuentas a cobrar' in concepto:
                kpis['deudores'] = {year: row[year] for year in self.years}
            elif 'vi. efectivo y otros activos líquidos' in concepto:
                kpis['efectivo'] = {year: row[year] for year in self.years}
            elif 'i. inmovilizado intangible' in concepto:
                kpis['inmovilizado_intangible'] = {year: row[year] for year in self.years}
            elif 'ii. inmovilizado material' in concepto:
                kpis['inmovilizado_material'] = {year: row[year] for year in self.years}

            # PATRIMONIO NETO Y PASIVO
            elif 'a) patrimonio neto' in concepto and 'total' not in concepto:
                kpis['patrimonio_neto'] = {year: row[year] for year in self.years}
            elif 'a-1) fondos propios' in concepto:
                kpis['fondos_propios'] = {year: row[year] for year in self.years}
            elif 'i. capital' in concepto and 'social' not in concepto:
                if 'capital' not in kpis:
                    kpis['capital'] = {year: row[year] for year in self.years}
            elif 'iii. reservas' in concepto and 'reservas' not in kpis:
                kpis['reservas'] = {year: row[year] for year in self.years}
            elif 'vii. resultado del ejercicio' in concepto:
                kpis['resultado_ejercicio_balance'] = {year: row[year] for year in self.years}
            elif 'b) pasivo no corriente' in concepto:
                kpis['pasivo_no_corriente'] = {year: row[year] for year in self.years}
            elif 'c) pasivo corriente' in concepto:
                kpis['pasivo_corriente'] = {year: row[year] for year in self.years}
            elif 'total patrimonio neto y pasivo' in concepto:
                kpis['total_pasivo_patrimonio'] = {year: row[year] for year in self.years}
            elif 'ii. deudas a largo plazo' in concepto:
                kpis['deudas_largo_plazo'] = {year: row[year] for year in self.years}
            elif 'ii. deudas a corto plazo' in concepto:
                kpis['deudas_corto_plazo'] = {year: row[year] for year in self.years}
            elif 'iv. acreedores comerciales y otras cuentas a pagar' in concepto:
                kpis['acreedores'] = {year: row[year] for year in self.years}

        return kpis

    def extract_detailed_activo(self) -> Dict:
        """Extrae detalle del Activo."""
        activo = {}

        categorias = [
            ('210 TERRENOS', 'Terrenos'),
            ('211 CONSTRUCCIONES', 'Construcciones'),
            ('212 INSTALACIONES', 'Instalaciones Técnicas'),
            ('213 MAQUINARIA', 'Maquinaria'),
            ('214 UTILLAJE', 'Utillaje'),
            ('215 OTRAS INSTALACIONES', 'Otras Instalaciones'),
            ('216 MOBILIARIO', 'Mobiliario'),
            ('217 EQUIPOS', 'Equipos Informáticos'),
            ('218 ELEMENTOS DE TRANSPORTE', 'Elementos de Transporte'),
        ]

        for idx, row in self.df.iterrows():
            concepto = str(row.get('Concepto', '')) if pd.notna(row.get('Concepto')) else ''

            for codigo, nombre in categorias:
                if codigo in concepto:
                    activo[nombre] = {year: row[year] for year in self.years}
                    break

        return activo

    def extract_detailed_pasivo(self) -> Dict:
        """Extrae detalle del Pasivo."""
        pasivo = {}

        for idx, row in self.df.iterrows():
            concepto = ''
            for col in ['Col1', 'Col2', 'Concepto']:
                if col in self.df.columns and pd.notna(row.get(col)):
                    concepto += ' ' + str(row.get(col, ''))
            concepto_lower = concepto.lower().strip()

            if '100 capital social' in concepto_lower:
                pasivo['Capital Social'] = {year: row[year] for year in self.years}
            elif '113 reservas voluntarias' in concepto_lower:
                pasivo['Reservas Voluntarias'] = {year: row[year] for year in self.years}
            elif '170 deudas a largo' in concepto_lower:
                pasivo['Deudas LP Entidades Crédito'] = {year: row[year] for year in self.years}
            elif '520 deudas corto plazo' in concepto_lower:
                pasivo['Deudas CP Entidades Crédito'] = {year: row[year] for year in self.years}
            elif '524 acreedores arrendamiento' in concepto_lower:
                pasivo['Arrendamiento Financiero CP'] = {year: row[year] for year in self.years}

        return pasivo


def calculate_financial_ratios(balance_kpis: Dict, pyg_kpis: Dict, years: List[str]) -> Dict:
    """
    Calcula ratios financieros combinando Balance y P&G.

    Args:
        balance_kpis: KPIs del Balance
        pyg_kpis: KPIs de P&G
        years: Lista de años

    Returns:
        Diccionario con ratios financieros
    """
    ratios = {}

    for year in years:
        year_ratios = {}

        # Obtener valores
        activo_total = balance_kpis.get('total_activo', {}).get(year, 0)
        activo_corriente = balance_kpis.get('activo_corriente', {}).get(year, 0)
        activo_no_corriente = balance_kpis.get('activo_no_corriente', {}).get(year, 0)
        pasivo_corriente = balance_kpis.get('pasivo_corriente', {}).get(year, 0)
        pasivo_no_corriente = balance_kpis.get('pasivo_no_corriente', {}).get(year, 0)
        patrimonio_neto = balance_kpis.get('patrimonio_neto', {}).get(year, 0)
        fondos_propios = balance_kpis.get('fondos_propios', {}).get(year, 0)
        existencias = balance_kpis.get('existencias', {}).get(year, 0)
        efectivo = balance_kpis.get('efectivo', {}).get(year, 0)
        deudores = balance_kpis.get('deudores', {}).get(year, 0)

        resultado_neto = pyg_kpis.get('resultado_neto', {}).get(year, 0)
        ingresos = pyg_kpis.get('ingresos', {}).get(year, 0)
        ebit = pyg_kpis.get('ebitda', {}).get(year, 0)

        pasivo_total = pasivo_corriente + pasivo_no_corriente

        # RATIOS DE LIQUIDEZ
        if pasivo_corriente > 0:
            year_ratios['ratio_liquidez'] = activo_corriente / pasivo_corriente
            year_ratios['ratio_acid_test'] = (activo_corriente - existencias) / pasivo_corriente
            year_ratios['ratio_tesoreria'] = efectivo / pasivo_corriente
        else:
            year_ratios['ratio_liquidez'] = 0
            year_ratios['ratio_acid_test'] = 0
            year_ratios['ratio_tesoreria'] = 0

        # RATIOS DE ENDEUDAMIENTO
        if activo_total > 0:
            year_ratios['ratio_endeudamiento'] = pasivo_total / activo_total
            year_ratios['ratio_autonomia'] = patrimonio_neto / activo_total
        else:
            year_ratios['ratio_endeudamiento'] = 0
            year_ratios['ratio_autonomia'] = 0

        if patrimonio_neto > 0:
            year_ratios['ratio_apalancamiento'] = pasivo_total / patrimonio_neto
        else:
            year_ratios['ratio_apalancamiento'] = 0

        # RATIOS DE RENTABILIDAD
        if patrimonio_neto > 0:
            year_ratios['roe'] = (resultado_neto / patrimonio_neto) * 100
        else:
            year_ratios['roe'] = 0

        if activo_total > 0:
            year_ratios['roa'] = (resultado_neto / activo_total) * 100
            year_ratios['rotacion_activos'] = ingresos / activo_total
        else:
            year_ratios['roa'] = 0
            year_ratios['rotacion_activos'] = 0

        if ingresos > 0:
            year_ratios['margen_neto'] = (resultado_neto / ingresos) * 100
        else:
            year_ratios['margen_neto'] = 0

        # RATIOS DE SOLVENCIA
        if pasivo_total > 0:
            year_ratios['ratio_solvencia'] = activo_total / pasivo_total
        else:
            year_ratios['ratio_solvencia'] = 0

        # FONDO DE MANIOBRA
        year_ratios['fondo_maniobra'] = activo_corriente - pasivo_corriente

        # CAPITAL CIRCULANTE SOBRE ACTIVO
        if activo_total > 0:
            year_ratios['capital_circulante_ratio'] = year_ratios['fondo_maniobra'] / activo_total
        else:
            year_ratios['capital_circulante_ratio'] = 0

        ratios[year] = year_ratios

    return ratios
