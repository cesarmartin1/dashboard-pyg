"""
Módulo de carga y procesamiento de datos para el Dashboard P&G.
"""

import pandas as pd
import re
import logging
from typing import Optional, List, Tuple
from io import BytesIO

logger = logging.getLogger(__name__)


class DataLoadError(Exception):
    """Error al cargar el archivo de datos."""
    pass


class ValidationError(Exception):
    """Error de validación de datos."""
    pass


class DataLoader:
    """
    Clase para cargar y procesar archivos Excel de P&G.

    Attributes:
        df: DataFrame con los datos procesados
        years: Lista de años detectados en el archivo
    """

    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.years: List[str] = []
        self._raw_df: Optional[pd.DataFrame] = None

    def load(self, file) -> pd.DataFrame:
        """
        Carga y procesa un archivo Excel de P&G.

        Args:
            file: Archivo subido (UploadedFile de Streamlit) o path

        Returns:
            DataFrame procesado

        Raises:
            DataLoadError: Si hay error al leer el archivo
            ValidationError: Si el formato no es válido
        """
        try:
            self._raw_df = pd.read_excel(file, sheet_name=0)
        except Exception as e:
            logger.error(f"Error al leer archivo Excel: {e}")
            raise DataLoadError(
                f"No se pudo leer el archivo Excel. "
                f"Asegúrate de que el archivo es un Excel válido (.xlsx o .xls). "
                f"Error: {str(e)}"
            )

        self._detect_and_rename_columns()
        self._clean_data()
        self._validate_structure()

        return self.df

    def _detect_and_rename_columns(self):
        """Detecta y renombra las columnas del DataFrame."""
        df = self._raw_df.copy()

        # Detectar columnas de años (4 dígitos que parecen años)
        year_pattern = re.compile(r'^(20\d{2}|19\d{2})$')
        year_columns = []
        other_columns = []

        for i, col in enumerate(df.columns):
            col_str = str(col).strip()
            if year_pattern.match(col_str):
                year_columns.append((i, col_str))
            else:
                other_columns.append((i, col))

        if not year_columns:
            # Intentar detectar años en las primeras filas
            for row_idx in range(min(5, len(df))):
                for col_idx, val in enumerate(df.iloc[row_idx]):
                    val_str = str(val).strip()
                    if year_pattern.match(val_str):
                        year_columns.append((col_idx, val_str))

        if not year_columns:
            # Asumir estructura por defecto si no se detectan años
            logger.warning("No se detectaron columnas de años, usando estructura por defecto")
            if len(df.columns) >= 10:
                df.columns = ['Col1', 'Concepto', 'Col3', 'Col4', 'Col5', 'Col6',
                              '2025', '2024', '2023', '2022']
                self.years = ['2025', '2024', '2023', '2022']
            else:
                raise ValidationError(
                    "No se pudo detectar la estructura del archivo. "
                    "El archivo debe contener columnas con años (ej: 2022, 2023, 2024, 2025)."
                )
        else:
            # Crear nuevo DataFrame con columnas renombradas
            self.years = sorted(set(col[1] for col in year_columns), reverse=True)

            # Buscar columna de concepto (generalmente la segunda o la que tiene texto)
            concepto_col = None
            for i, col in enumerate(df.columns):
                if i not in [yc[0] for yc in year_columns]:
                    sample_values = df.iloc[:20, i].dropna()
                    if len(sample_values) > 0:
                        text_count = sum(1 for v in sample_values
                                         if isinstance(v, str) and len(v) > 5)
                        if text_count > len(sample_values) * 0.5:
                            concepto_col = i
                            break

            if concepto_col is None:
                concepto_col = 1 if len(df.columns) > 1 else 0

            # Construir nuevo DataFrame
            columns_to_keep = {'Concepto': concepto_col}
            for idx, year in year_columns:
                columns_to_keep[year] = idx

            new_df = pd.DataFrame()
            for name, idx in columns_to_keep.items():
                new_df[name] = df.iloc[:, idx]

            df = new_df

        # Si no se detectaron años, usar valores por defecto
        if not self.years:
            self.years = ['2025', '2024', '2023', '2022']

        self.df = df

    def _clean_data(self):
        """Limpia los datos del DataFrame."""
        if self.df is None:
            return

        # Mantener todas las columnas (texto + años)
        # No filtrar solo Concepto, ya que los KPIs pueden estar en otras columnas

        # Convertir valores a numérico en columnas de años
        for year in self.years:
            if year in self.df.columns:
                self.df[year] = pd.to_numeric(self.df[year], errors='coerce').fillna(0)

    def _validate_structure(self):
        """Valida la estructura del DataFrame."""
        if self.df is None or len(self.df) == 0:
            raise ValidationError(
                "El archivo está vacío o no contiene datos válidos."
            )

        year_cols = [y for y in self.years if y in self.df.columns]
        if not year_cols:
            raise ValidationError(
                "No se encontraron columnas de años en el archivo. "
                f"Años esperados: {self.years}"
            )

        # Verificar que hay al menos algunos datos numéricos
        total_values = 0
        for year in year_cols:
            total_values += (self.df[year] != 0).sum()

        if total_values == 0:
            raise ValidationError(
                "El archivo no contiene valores numéricos. "
                "Verifica que las columnas de años contienen datos."
            )

        logger.info(f"Archivo cargado correctamente: {len(self.df)} filas, "
                    f"años: {year_cols}")

    def get_years(self) -> List[str]:
        """Retorna la lista de años disponibles."""
        return self.years

    def get_dataframe(self) -> pd.DataFrame:
        """Retorna el DataFrame procesado."""
        if self.df is None:
            raise DataLoadError("No hay datos cargados.")
        return self.df
