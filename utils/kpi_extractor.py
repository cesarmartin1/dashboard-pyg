"""
Módulo de extracción de KPIs para el Dashboard P&G.
"""

import pandas as pd
import re
import logging
from typing import Dict, Any, List, Optional, Tuple

from config.kpi_mappings import KPI_MAPPINGS, DETAILED_MAPPINGS, match_pattern

logger = logging.getLogger(__name__)


class KPIExtractor:
    """
    Extrae KPIs de un DataFrame de P&G usando patrones flexibles.

    Attributes:
        df: DataFrame con los datos
        years: Lista de años disponibles
        kpis: Diccionario de KPIs extraídos
    """

    def __init__(self, df: pd.DataFrame, years: List[str]):
        self.df = df
        self.years = years
        self.kpis: Dict[str, Dict[str, float]] = {}
        self._not_found: List[str] = []
        self._found: List[str] = []

    def extract_all(self) -> Dict[str, Dict[str, float]]:
        """
        Extrae todos los KPIs definidos en la configuración.

        Returns:
            Diccionario con los KPIs extraídos

        Raises:
            ValueError: Si faltan KPIs requeridos
        """
        for kpi_name, config in KPI_MAPPINGS.items():
            value = self._find_kpi(kpi_name, config)
            if value is not None:
                self.kpis[kpi_name] = value
                self._found.append(kpi_name)
            elif config.get('required', False):
                self._not_found.append(kpi_name)
                logger.warning(f"KPI requerido no encontrado: {kpi_name}")
            else:
                # Usar valor por defecto
                default = config.get('default', 0)
                self.kpis[kpi_name] = {year: default for year in self.years}

        if self._not_found:
            logger.warning(f"KPIs no encontrados: {self._not_found}")

        return self.kpis

    def _find_kpi(self, kpi_name: str, config: dict) -> Optional[Dict[str, float]]:
        """
        Busca un KPI en el DataFrame.

        Args:
            kpi_name: Nombre del KPI
            config: Configuración del KPI (patterns, sign, etc.)

        Returns:
            Diccionario con valores por año o None si no se encuentra
        """
        patterns = config.get('patterns', [])
        sign = config.get('sign', 1)

        for idx, row in self.df.iterrows():
            # Buscar en todas las columnas de texto, no solo en Concepto
            found = False
            for col in row.index:
                if col in self.years:
                    continue
                cell_value = str(row.get(col, ''))
                if cell_value and match_pattern(cell_value, patterns):
                    found = True
                    break

            if found:
                result = {}
                for year in self.years:
                    if year in row.index:
                        value = row[year]
                        if pd.isna(value):
                            value = 0
                        if sign == -1:
                            value = abs(value)
                        result[year] = value
                    else:
                        result[year] = 0

                logger.debug(f"KPI '{kpi_name}' encontrado en fila {idx}")
                return result

        return None

    def extract_detailed_data(self) -> Tuple[Dict, Dict, Dict, Dict]:
        """
        Extrae datos detallados (servicios, gastos, etc.).

        Returns:
            Tupla con (servicios, aprovisionamientos, personal, otros_gastos)
        """
        servicios = self._extract_servicios()
        aprovisionamientos = self._extract_aprovisionamientos()
        personal = self._extract_personal()
        otros_gastos = self._extract_otros_gastos()

        return servicios, aprovisionamientos, personal, otros_gastos

    def _extract_servicios(self) -> Dict[str, Dict[str, float]]:
        """Extrae ingresos por tipo de servicio."""
        servicios = {}
        config = DETAILED_MAPPINGS.get('servicios', {})
        parent_pattern = config.get('parent_pattern', r'705\s+PRESTACIONES')
        item_pattern = config.get('item_pattern', r'^705\.0\.0\.')
        stop_pattern = config.get('stop_pattern', r'2\.\s*Variaci')

        in_servicios = False

        for idx, row in self.df.iterrows():
            concepto = str(row.get('Concepto', ''))
            if not concepto:
                continue

            if re.search(parent_pattern, concepto, re.IGNORECASE):
                in_servicios = True
                continue

            if in_servicios:
                if re.search(stop_pattern, concepto, re.IGNORECASE):
                    in_servicios = False
                    continue

                if re.match(item_pattern, concepto):
                    # Extraer nombre del servicio
                    nombre = re.sub(item_pattern, '', concepto).strip()
                    if ' ' in nombre:
                        nombre = nombre.split(' ', 1)[-1]

                    servicios[nombre] = {
                        year: row.get(year, 0) for year in self.years
                    }

        return servicios

    def _extract_aprovisionamientos(self) -> Dict[str, Dict[str, float]]:
        """Extrae detalle de aprovisionamientos."""
        aprovisionamientos = {}
        config = DETAILED_MAPPINGS.get('aprovisionamientos_detalle', {})
        item_pattern = config.get('item_pattern', r'^602\.0\.0\.')

        for idx, row in self.df.iterrows():
            concepto = str(row.get('Concepto', ''))
            if not concepto:
                continue

            if re.match(item_pattern, concepto):
                nombre = re.sub(item_pattern, '', concepto).strip()
                if ' ' in nombre:
                    nombre = nombre.split(' ', 1)[-1]

                aprovisionamientos[nombre] = {
                    year: abs(row.get(year, 0)) for year in self.years
                }

        return aprovisionamientos

    def _extract_personal(self) -> Dict[str, Dict[str, float]]:
        """Extrae detalle de gastos de personal."""
        personal = {}
        config = DETAILED_MAPPINGS.get('personal_detalle', {})
        categories = config.get('categories', [])

        for idx, row in self.df.iterrows():
            concepto = str(row.get('Concepto', ''))
            if not concepto:
                continue

            for pattern, nombre in categories:
                if re.search(pattern, concepto, re.IGNORECASE):
                    personal[nombre] = {
                        year: abs(row.get(year, 0)) for year in self.years
                    }
                    break

        return personal

    def _extract_otros_gastos(self) -> Dict[str, Dict[str, float]]:
        """Extrae detalle de otros gastos."""
        otros_gastos = {}
        config = DETAILED_MAPPINGS.get('otros_gastos_detalle', {})
        categories = config.get('categories', [])

        for idx, row in self.df.iterrows():
            concepto = str(row.get('Concepto', ''))
            if not concepto:
                continue

            for pattern, nombre in categories:
                if re.search(pattern, concepto, re.IGNORECASE):
                    otros_gastos[nombre] = {
                        year: abs(row.get(year, 0)) for year in self.years
                    }
                    break

        return otros_gastos

    def get_missing_kpis(self) -> List[str]:
        """Retorna lista de KPIs requeridos no encontrados."""
        return self._not_found

    def get_found_kpis(self) -> List[str]:
        """Retorna lista de KPIs encontrados."""
        return self._found
