"""Tabla de posiciones del torneo."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from pool.services.leaderboard import build_leaderboard
from pool.views.stages import tabs_context


@login_required
def leaderboard_view(request: HttpRequest) -> HttpResponse:
    context = {"rows": build_leaderboard(), **tabs_context(request.user)}
    return render(request, "leaderboard.html", context)
