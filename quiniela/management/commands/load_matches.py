"""Carga partidos desde db/jsons/matches.json (idempotente)."""

import json
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from quiniela.models import Match, Team

JSON_PATH = Path(settings.BASE_DIR) / "db" / "jsons" / "matches.json"

# El JSON mezcla dos formatos de fecha: con coma y sin coma.
DATE_FORMATS = ("%Y-%m-%d, %H:%M", "%Y-%m-%d %H:%M")


def parse_match_date(raw: str) -> datetime:
    """Convierte la cadena de fecha en un datetime timezone-aware.

    Acepta tanto "%Y-%m-%d, %H:%M" como "%Y-%m-%d %H:%M".
    """
    for fmt in DATE_FORMATS:
        try:
            naive = datetime.strptime(raw, fmt)
        except ValueError:
            continue
        return timezone.make_aware(naive)
    raise ValueError(f"Formato de fecha no reconocido: {raw!r}")


class Command(BaseCommand):
    help = "Carga los partidos desde matches.json de forma idempotente."

    def handle(self, *args, **options) -> None:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            matches = json.load(f)

        team_map = {team.name: team for team in Team.objects.all()}

        created_count = 0
        for item in matches:
            team_a = team_map[item["team_a"]]
            team_b = team_map[item["team_b"]]
            date = parse_match_date(item["date"])

            _, created = Match.objects.get_or_create(
                team_a=team_a,
                team_b=team_b,
                date=date,
                defaults={
                    "phase": "groups",
                    "group_name": item["group"],
                    "stadium": item.get("stadium"),
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Partidos creados: {created_count} "
            f"(de {len(matches)} en el archivo)."
        ))
