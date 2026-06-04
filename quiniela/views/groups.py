"""Vistas de la fase de grupos de la quiniela."""

from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from quiniela.models import Match, Prediction, User
from quiniela.utils import convert_date


def render_matches_by_group(user: User) -> dict[str, list[Match]]:
    """Agrupa los partidos de fase 'groups' por su 'group_name'.

    Para cada partido adjunta (como atributos en memoria) la fecha
    formateada y, si el usuario ya predijo, los goles predichos. Usa
    select_related en team_a/team_b para evitar consultas N+1, ya que
    el template accede a match.team_a.name y match.team_b.name.
    """
    matches = (
        Match.objects.filter(phase="groups")
        .select_related("team_a", "team_b")
    )

    # Indexamos las predicciones del usuario por match_id para hacer
    # el cruce en memoria (una sola consulta).
    predictions = Prediction.objects.filter(user=user)
    predictions_by_match = {p.match_id: p for p in predictions}

    groups: dict[str, list[Match]] = defaultdict(list)
    for match in matches:
        prediction = predictions_by_match.get(match.id)
        if prediction is not None:
            match.predicted_a = prediction.goals_a
            match.predicted_b = prediction.goals_b
        match.formatted_date = convert_date(match.date)
        groups[match.group_name].append(match)

    return groups


@login_required
def grupos(request: HttpRequest) -> HttpResponse:
    """Renderiza la fase de grupos con las predicciones del usuario.

    'still_submitting' es True mientras el usuario no haya enviado
    (submitted) ninguna predicción de la fase de grupos; controla si
    aún puede editar y enviar sus pronósticos.
    """
    groups = render_matches_by_group(request.user)
    still_submitting = not Prediction.objects.filter(
        user=request.user,
        match__phase="groups",
        status="submitted",
    ).exists()
    context = {
        "groups": groups,
        "user": request.user,
        "still_submitting": still_submitting,
    }
    return render(request, "grupos.html", context)
