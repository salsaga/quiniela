"""Carga equipos desde db/jsons/teams.json (idempotente)."""

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from quiniela.models import Team

JSON_PATH = Path(settings.BASE_DIR) / "db" / "jsons" / "teams.json"


class Command(BaseCommand):
    help = "Carga los equipos desde teams.json de forma idempotente."

    def handle(self, *args, **options) -> None:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            teams = json.load(f)

        created_count = 0
        for item in teams:
            _, created = Team.objects.get_or_create(
                name=item["team_name"],
                defaults={
                    "flag": item.get("flag"),
                    "group_name": item["group_name"],
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Equipos creados: {created_count} "
            f"(de {len(teams)} en el archivo)."
        ))
