"""Simula un torneo en curso sobre la base de datos local.

Deja la DB como si hoy fuera el día ``--day`` del Mundial (default 5):
desplaza el calendario completo para que el día 1 caiga ``day - 1``
días atrás, fabrica resultados plausibles para los partidos ya
"jugados" (marcador, tarjetas y un ``raw_fd`` con formato del endpoint
detail de football-data: ``goals[]`` y ``bookings[]``), completa las
predicciones de grupos de los usuarios activos y marca sus envíos.

Idempotente: el desplazamiento se ancla a una fecha absoluta y los
datos ya generados no se vuelven a tocar (salvo ``--rebuild-results``).

SOLO para la DB local. Respalda antes:  cp db/app.sqlite3 db/app.sqlite3.bak
"""

import random
from datetime import datetime, time, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from pool.models import Prediction, StageUser, User
from tournament.models import Match, Stage

# Distribución plausible de goles por equipo en un partido.
GOAL_WEIGHTS = {0: 25, 1: 35, 2: 22, 3: 12, 4: 5, 5: 1}
YELLOW_WEIGHTS = {0: 15, 1: 35, 2: 30, 3: 15, 4: 5}
RED_PROBABILITY = 0.07

FIRST_INITIALS = list("ABCDEFGHIJLMNOPRST")
SURNAMES = [
    "Sánchez", "Goleador", "Da Silva", "Petrov", "Yamada", "Okafor",
    "Johansson", "Kovač", "Mbemba", "Rossi", "Dupont", "Kim",
    "Hernández", "Schmidt", "Nakamura", "Diallo", "Pereira", "Novak",
]


def _weighted(rng: random.Random, weights: dict[int, int]) -> int:
    values = list(weights)
    return rng.choices(values, weights=[weights[v] for v in values])[0]


def _scorer_name(rng: random.Random, tla: str) -> str:
    initial = rng.choice(FIRST_INITIALS)
    surname = rng.choice(SURNAMES)
    return f"{initial}. {surname} ({tla})"


def _fake_raw_fd(rng: random.Random, match: Match) -> dict:
    """Snapshot estilo FD detail coherente con los campos del modelo."""

    def team_payload(team):
        return {"id": team.fd_id, "name": team.name, "tla": team.fifa_code}

    goals = []
    for team, count in (
        (match.home_team, match.home_goals),
        (match.away_team, match.away_goals),
    ):
        for _ in range(count):
            goals.append({
                "minute": rng.randint(1, 90),
                "team": {"id": team.fd_id},
                "scorer": {"name": _scorer_name(rng, team.fifa_code)},
            })
    goals.sort(key=lambda g: g["minute"])

    bookings = []
    for team, yellows, reds in (
        (match.home_team, match.home_yellow, match.home_red),
        (match.away_team, match.away_yellow, match.away_red),
    ):
        for card, count in (("YELLOW", yellows), ("RED", reds)):
            for _ in range(count):
                bookings.append({
                    "minute": rng.randint(1, 90),
                    "team": {"id": team.fd_id},
                    "card": card,
                })
    bookings.sort(key=lambda b: b["minute"])

    diff = match.home_goals - match.away_goals
    winner = "DRAW" if diff == 0 else ("HOME_TEAM" if diff > 0 else "AWAY_TEAM")
    group = (
        f"GROUP_{match.home_team.group_name}"
        if match.stage.key == "GROUP_STAGE" else None
    )
    return {
        "id": match.fd_id,
        "utcDate": match.datetime.isoformat(),
        "status": "FINISHED",
        "stage": match.stage.key,
        "group": group,
        "homeTeam": team_payload(match.home_team),
        "awayTeam": team_payload(match.away_team),
        "score": {
            "winner": winner,
            "duration": "REGULAR",
            "fullTime": {"home": match.home_goals, "away": match.away_goals},
        },
        "goals": goals,
        "bookings": bookings,
        "simulated": True,
    }


class Command(BaseCommand):
    help = (
        "Simula torneo en curso: corre el calendario para que hoy sea el "
        "día 3, fabrica resultados de los días previos y marca envíos. "
        "Respalda antes: cp db/app.sqlite3 db/app.sqlite3.bak"
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--day", type=int, default=5,
            help="Día del Mundial que será HOY (hora de CDMX). Default: 5.",
        )
        parser.add_argument("--seed", type=int, default=2026)
        parser.add_argument(
            "--rebuild-results", action="store_true",
            help="Regenera resultados aunque el partido ya esté FINISHED.",
        )

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        rng = random.Random(options["seed"])
        if options["day"] < 1:
            raise CommandError("--day debe ser >= 1.")
        today = timezone.localdate()

        matches = list(Match.objects.order_by("datetime", "of_number"))
        if not matches:
            raise CommandError("No hay partidos; corre los seeds primero.")

        delta_days = self._shift_calendar(matches, today, options["day"])
        finished = self._fabricate_results(rng, matches, today, options["rebuild_results"])
        deadline = self._configure_group_stage(matches)
        created_su = self._sync_stage_users()
        created_preds = self._fill_predictions(rng, deadline)
        marked_sent = self._mark_sent(rng, deadline)

        self.stdout.write(self.style.SUCCESS(
            f"Calendario desplazado {delta_days:+d} día(s) (hoy = día "
            f"{options['day']}). Resultados fabricados: {finished}. "
            f"StageUser creados: {created_su}. Predicciones creadas: "
            f"{created_preds}. Envíos marcados: {marked_sent}."
        ))

    def _shift_calendar(self, matches: list[Match], today, day: int) -> int:
        """Ancla el día 1 a (hoy - (day-1)): re-ejecutar da delta 0."""
        current_day1 = timezone.localdate(matches[0].datetime)
        delta = (today - timedelta(days=day - 1)) - current_day1
        if delta:
            for match in matches:
                match.datetime += delta
            Match.objects.bulk_update(matches, ["datetime"], batch_size=200)
        return delta.days

    def _fabricate_results(
        self, rng: random.Random, matches: list[Match], today, rebuild: bool
    ) -> int:
        count = 0
        for match in matches:
            if timezone.localdate(match.datetime) >= today:
                continue
            if match.home_team is None or match.away_team is None:
                continue
            if match.status == "FINISHED" and not rebuild:
                continue
            match.home_goals = _weighted(rng, GOAL_WEIGHTS)
            match.away_goals = _weighted(rng, GOAL_WEIGHTS)
            match.home_yellow = _weighted(rng, YELLOW_WEIGHTS)
            match.away_yellow = _weighted(rng, YELLOW_WEIGHTS)
            match.home_red = int(rng.random() < RED_PROBABILITY)
            match.away_red = int(rng.random() < RED_PROBABILITY)
            match.status = "FINISHED"
            match.decided_by = Match.REGULAR
            match.raw_fd = _fake_raw_fd(rng, match)
            match.save()
            count += 1
        return count

    def _configure_group_stage(self, matches: list[Match]):
        """Cierra la fase de grupos.

        Regla (ver reglas.html): la quiniela cierra a las 11:59 pm del
        día previo al primer partido, en hora de CDMX.
        """
        day_before = timezone.localdate(matches[0].datetime) - timedelta(days=1)
        deadline = timezone.make_aware(
            datetime.combine(day_before, time(23, 59))
        )
        Stage.objects.filter(key="GROUP_STAGE").update(
            opens_at=deadline - timedelta(days=30),
            send_deadline=deadline,
        )
        return deadline

    def _sync_stage_users(self) -> int:
        stages = list(Stage.objects.all())
        existing = set(StageUser.objects.values_list("user_id", "stage_id"))
        to_create = [
            StageUser(user=user, stage=stage)
            for user in User.objects.all()
            for stage in stages
            if (user.id, stage.id) not in existing
        ]
        StageUser.objects.bulk_create(to_create)
        return len(to_create)

    def _fill_predictions(self, rng: random.Random, deadline) -> int:
        """Completa las predicciones de grupos de los usuarios activos.

        Respeta las existentes; los inactivos no predicen (quedan LOCKED).
        """
        group_matches = list(Match.objects.filter(stage__key="GROUP_STAGE"))
        existing = set(Prediction.objects.values_list("user_id", "match_id"))
        to_create = []
        for user in User.objects.filter(is_active=True):
            for match in group_matches:
                if (user.id, match.id) in existing:
                    continue
                to_create.append(Prediction(
                    user=user,
                    match=match,
                    home_goals=_weighted(rng, GOAL_WEIGHTS),
                    away_goals=_weighted(rng, GOAL_WEIGHTS),
                    date=deadline - timedelta(minutes=rng.randint(10, 700)),
                ))
        Prediction.objects.bulk_create(to_create)
        return len(to_create)

    def _mark_sent(self, rng: random.Random, deadline) -> int:
        """Marca envíos pendientes y corrige los que quedaron obsoletos.

        Tras re-anclar el calendario el deadline puede haber retrocedido,
        dejando ``sent_at`` posteriores a él; se regeneran también.
        """
        rows = StageUser.objects.filter(
            Q(sent_at__isnull=True) | Q(sent_at__gt=deadline),
            stage__key="GROUP_STAGE",
            user__is_active=True,
        ).select_related("user")
        count = 0
        for row in rows:
            row.sent_at = deadline - timedelta(minutes=rng.randint(5, 600))
            row.save(update_fields=["sent_at"])
            count += 1
        return count
