"""Rutas de la app pool (quiniela)."""

from django.urls import path

from pool.views import auth, leaderboard, matches, predictions, stages

urlpatterns = [
    path("login/", auth.login_view, name="login"),
    path("logout/", auth.logout_view, name="logout"),
    path("reglas/", stages.reglas, name="reglas"),
    path("posiciones/", leaderboard.leaderboard_view, name="standings"),
    path("partidos/", matches.matches_by_day, name="matches"),
    path("stage/<str:key>/", stages.stage_view, name="stage"),
    path("save/", predictions.save_predictions, name="save"),
    path(
        "prediction/<int:match_id>/",
        predictions.save_prediction,
        name="save_prediction",
    ),
    path("send/", predictions.send_predictions, name="send"),
    path("", stages.root_redirect, name="root"),
]
