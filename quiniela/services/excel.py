"""Servicio de generación y envío del Excel de predicciones."""

from io import BytesIO

from django.core.mail import EmailMessage
from openpyxl import Workbook

from quiniela.views.groups import render_matches_by_group

XLSX_MIMETYPE = (
    "application/vnd.openxmlformats-officedocument"
    ".spreadsheetml.sheet"
)

HEADER_ROW = [
    "Equipo A",
    "Goles A",
    "Goles B",
    "Equipo B",
    "Fecha",
    "Sede",
]

EMAIL_SUBJECT = "Tus predicciones"
EMAIL_BODY = (
    "Te adjunto el excel de tus predicciones de la fase de "
    "grupos. Saludos!"
)


def generate_excel(user) -> None:
    """Genera el Excel de predicciones y lo envía por correo.

    Construye un ``Workbook`` local (uno por llamada, para evitar
    el bug del libro global que acumulaba hojas entre peticiones),
    crea una hoja por grupo con ``render_matches_by_group(user)``,
    serializa el archivo en memoria y lo adjunta a un correo
    dirigido a ``user.email``.
    """
    workbook = Workbook()
    workbook.remove(workbook.active)

    groups = render_matches_by_group(user)
    for group_name, matches in groups.items():
        sheet = workbook.create_sheet(title=f"Grupo {group_name}")
        sheet.append(HEADER_ROW)
        for match in matches:
            predicted_a = getattr(match, "predicted_a", 0)
            predicted_b = getattr(match, "predicted_b", 0)
            sheet.append([
                match.team_a.name,
                predicted_a,
                predicted_b,
                match.team_b.name,
                match.formatted_date,
                match.stadium,
            ])

    buffer = BytesIO()
    workbook.save(buffer)

    message = EmailMessage(
        subject=EMAIL_SUBJECT,
        body=EMAIL_BODY,
        to=[user.email],
    )
    message.attach("predicciones.xlsx", buffer.getvalue(), XLSX_MIMETYPE)
    message.send()
