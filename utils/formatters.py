"""
Funciones de formateo para el Dashboard P&G.
"""


def format_currency(value: float, decimals: int = 0) -> str:
    """
    Formatea un valor numérico como moneda en euros.

    Args:
        value: Valor numérico a formatear
        decimals: Número de decimales (por defecto 0)

    Returns:
        String formateado como moneda (ej: "1.234.567 EUR")
    """
    try:
        if decimals == 0:
            return f"{value:,.0f} EUR".replace(",", ".")
        formatted = f"{value:,.{decimals}f}"
        # Convertir formato inglés a español (1,234.56 -> 1.234,56)
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted} EUR"
    except (ValueError, TypeError):
        return "0 EUR"


def calculate_variation(current: float, previous: float) -> float:
    """
    Calcula la variación porcentual entre dos valores.

    Args:
        current: Valor actual
        previous: Valor anterior

    Returns:
        Variación porcentual (ej: 15.5 para +15.5%)
    """
    try:
        if previous == 0:
            if current == 0:
                return 0.0
            return 100.0 if current > 0 else -100.0
        return ((current - previous) / abs(previous)) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Formatea un valor como porcentaje.

    Args:
        value: Valor numérico (ya en porcentaje, ej: 15.5)
        decimals: Número de decimales

    Returns:
        String formateado como porcentaje (ej: "15,5%")
    """
    try:
        formatted = f"{value:.{decimals}f}".replace(".", ",")
        return f"{formatted}%"
    except (ValueError, TypeError):
        return "0%"


def format_variation(value: float, decimals: int = 1) -> str:
    """
    Formatea una variación con signo.

    Args:
        value: Valor de variación
        decimals: Número de decimales

    Returns:
        String formateado con signo (ej: "+15,5%" o "-3,2%")
    """
    try:
        sign = "+" if value >= 0 else ""
        formatted = f"{value:.{decimals}f}".replace(".", ",")
        return f"{sign}{formatted}%"
    except (ValueError, TypeError):
        return "0%"
