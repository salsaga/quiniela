"""Funciones auxiliares de presentación para la quiniela."""

from datetime import datetime

MONTHS_ES: dict[int, str] = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}


WEEKDAYS_ES: dict[int, str] = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo",
}


def format_weekday_day(date: datetime) -> str:
    """Formatea como '{Día de semana} {día} de {mes}' en español."""
    return f"{WEEKDAYS_ES[date.weekday()]} {date.day} de {MONTHS_ES[date.month]}"


def format_day(date: datetime) -> str:
    """Formatea la fecha como '{día} de {mes}' (mes en español)."""
    return f"{date.day} de {MONTHS_ES[date.month]}"


def format_time(date: datetime) -> str:
    """Formatea la hora en 24 h con ceros a la izquierda ('HH:MM')."""
    return date.strftime("%H:%M")
