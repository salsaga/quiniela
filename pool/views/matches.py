"""Vista dinámica de partidos ordenados por día calendario (CDMX).

Una sola página con todos los partidos agrupados por día (zona horaria
del proyecto, America/Mexico_City): los días pasados quedan arriba, los
futuros abajo, y matchday.js posiciona el scroll en el día de hoy.
"""

from collections import defaultdict
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from pool.models import Prediction
from pool.services.scoring import ScoreDetail, score_detail
from pool.utils import format_time, format_weekday_day
from pool.views.stages import annotate_result, tabs_context
from tournament.models import Match


def _scorers(match: Match) -> tuple[list[str], list[str]]:
    """Goleadores ("35' Fulano") por equipo desde ``raw_fd["goals"]``.

    El formato es el del endpoint detail de FD; si el snapshot no trae
    goles (p. ej. solo se sincronizó el list endpoint) degrada a listas
    vacías sin romper la página.
    """
    raw = match.raw_fd or {}
    home_id = (raw.get("homeTeam") or {}).get("id")
    home, away = [], []
    for goal in raw.get("goals") or []:
        scorer = (goal.get("scorer") or {}).get("name", "")
        line = f"{goal.get('minute', '?')}' {scorer}".strip()
        if (goal.get("team") or {}).get("id") == home_id:
            home.append(line)
        else:
            away.append(line)
    return home, away


def _points_breakdown(detail: ScoreDetail, is_draw: bool) -> list[tuple]:
    """Desglose aditivo de los puntos: las líneas suman el total."""
    if detail.points == 0:
        return [("Resultado errado", "0")]
    lines = [("Empate acertado" if is_draw else "Ganador acertado", "+3")]
    if not is_draw and (detail.diff_bonus or detail.exact):
        lines.append(("Diferencia exacta", "+1"))
    if detail.exact:
        lines.append(("Marcador exacto", "+1"))
    return lines


@login_required
def matches_by_day(request: HttpRequest) -> HttpResponse:
    today = timezone.localdate()
    matches = list(
        Match.objects.select_related(
            "home_team", "away_team", "stage", "stadium"
        ).order_by("datetime", "of_number")
    )
    own = {
        p.match_id: p for p in Prediction.objects.filter(user=request.user)
    }

    # Predicciones rivales: solo de fases ya cerradas (antes del deadline
    # las predicciones ajenas son privadas).
    closed_stages = {m.stage_id for m in matches if m.stage.is_past_deadline}
    rivals: dict[int, list[Prediction]] = defaultdict(list)
    if closed_stages:
        rival_rows = (
            Prediction.objects.filter(match__stage_id__in=closed_stages)
            .select_related("user")
            .order_by("user__first_name")
        )
        for pred in rival_rows:
            rivals[pred.match_id].append(pred)

    grouped: dict = defaultdict(list)
    for match in matches:
        prediction = own.get(match.id)
        annotate_result(match, prediction)
        if prediction is not None:
            match.predicted_home = prediction.home_goals
            match.predicted_away = prediction.away_goals

        if match.stage.key == "GROUP_STAGE":
            match.phase_label = f"Grupo {match.home_team.group_name}"
        else:
            match.phase_label = match.name or match.stage.name

        local_dt = match.datetime + timedelta(hours=match.stadium.utc_offset)
        match.local_time = format_time(local_dt)

        if match.is_finished:
            match.home_scorers, match.away_scorers = _scorers(match)
            if prediction is not None:
                detail = score_detail(
                    prediction.home_goals, prediction.away_goals,
                    match.home_goals, match.away_goals,
                )
                match.points_lines = _points_breakdown(
                    detail, match.home_goals == match.away_goals
                )

        match.rival_predictions = [
            {
                "name": pred.user.first_name or pred.user.email,
                "home": pred.home_goals,
                "away": pred.away_goals,
                "detail": (
                    score_detail(pred.home_goals, pred.away_goals,
                                 match.home_goals, match.away_goals)
                    if match.is_finished else None
                ),
            }
            for pred in rivals.get(match.id, [])
        ]
        grouped[timezone.localdate(match.datetime)].append(match)

    days = [
        {
            "date": date,
            "label": format_weekday_day(date),
            "is_today": date == today,
            "is_past": date < today,
            "matches": grouped[date],
        }
        for date in sorted(grouped)
    ]
    context = {"days": days, "today": today, **tabs_context(request.user)}
    return render(request, "matchday.html", context)
