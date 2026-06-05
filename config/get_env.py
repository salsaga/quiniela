"""Lectura tipada de variables de entorno (parsing + defaults)."""
import os
from pathlib import Path


def getenv_list(
    name: str, default: list[str] | None = None
) -> list[str] | None:
    """Lista separada por comas; ``default`` si la variable no existe."""
    value = os.getenv(name)
    if value is None:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def getenv_bool(name: str, default: bool = False) -> bool:
    """``True`` si vale 1/true/yes/on (insensible a mayúsculas)."""
    value = os.getenv(name)
    if not value:
        return default
    return value.lower() in ("1", "true", "yes", "on")


def getenv_int(name: str, default: int = 0) -> int:
    """Entero; ``default`` si la variable falta o no es numérica."""
    value = os.getenv(name)
    if not value or not value.lstrip("-").isdigit():
        return default
    return int(value)


def getenv_db(
    env_pref: str = "POSTGRES", sqlite_path: str | Path = "db.sqlite3"
) -> dict:
    """Config de BD: Postgres si ``{env_pref}_DB`` existe; si no, SQLite.

    El prefijo agrupa las variables (``POSTGRES_DB``, ``POSTGRES_USER``…),
    igual que el patrón del proyecto OCS, para no repetir el bloque.
    """
    name = os.getenv(f"{env_pref}_DB")
    if name:
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": name,
            "USER": os.getenv(f"{env_pref}_USER"),
            "PASSWORD": os.getenv(f"{env_pref}_PASSWORD"),
            "HOST": os.getenv(f"{env_pref}_HOST", "localhost"),
            "PORT": getenv_int(f"{env_pref}_PORT", 5432),
        }
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": sqlite_path,
    }