"""Cálculo de puntos de un pronóstico contra el resultado real.

Reglas (ver ``templates/reglas.html``, documentadas para los jugadores):

- Acertar ganador o empate: 3 puntos.
- Acertar también la diferencia de goles (no aplica en empates): +1 punto.
- Marcador exacto: 5 puntos totales si hubo ganador, 4 si fue empate.

En eliminatorias se compara el marcador en tiempo regular/extra
(``Match.home_goals``/``away_goals``), nunca los penales.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreDetail:
    """Puntos con desglose. ``exact`` y ``diff_bonus`` son disjuntos:
    un 4 puede ser exacto-empate o ganador+diferencia, así que los
    conteos deben salir de estos flags, nunca del valor numérico.
    """

    points: int
    exact: bool
    diff_bonus: bool


def score_detail(
    pred_home: int | None,
    pred_away: int | None,
    actual_home: int | None,
    actual_away: int | None,
) -> ScoreDetail | None:
    """ "sin resultado" no es lo mismo que
    "cero puntos".
    """
    if None in (pred_home, pred_away, actual_home, actual_away):
        return None

    pred_diff = pred_home - pred_away
    actual_diff = actual_home - actual_away

    def _outcome(diff: int) -> int:
        return 0 if diff == 0 else (1 if diff > 0 else -1)

    if _outcome(pred_diff) != _outcome(actual_diff):
        return ScoreDetail(points=0, exact=False, diff_bonus=False)

    is_draw = actual_diff == 0
    exact = pred_home == actual_home and pred_away == actual_away
    if exact:
        return ScoreDetail(points=4 if is_draw else 5, exact=True,
                           diff_bonus=False)

    diff_bonus = not is_draw and pred_diff == actual_diff
    return ScoreDetail(points=4 if diff_bonus else 3, exact=False,
                       diff_bonus=diff_bonus)


def calculate_points(
    pred_home: int | None,
    pred_away: int | None,
    actual_home: int | None,
    actual_away: int | None,
) -> int | None:
    detail = score_detail(pred_home, pred_away, actual_home, actual_away)
    return detail.points if detail else None
