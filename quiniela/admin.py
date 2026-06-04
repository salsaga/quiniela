from django.contrib import admin

from .models import Match, Prediction, Team, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin simple de usuarios.

    No usa el ``UserAdmin`` clásico de Django para evitar el manejo del
    campo ``password`` inusable de los usuarios preregistrados.
    """

    list_display = (
        "email",
        "username",
        "first_name",
        "is_active",
        "did_pay",
    )
    search_fields = ("email",)


admin.site.register(Team)
admin.site.register(Match)
admin.site.register(Prediction)
