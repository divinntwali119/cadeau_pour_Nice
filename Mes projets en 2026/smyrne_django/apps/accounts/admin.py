from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import ProfilMembre


class ProfilMembreInline(admin.StackedInline):
    model = ProfilMembre
    can_delete = False
    verbose_name_plural = 'Profil du membre'


class UserAdmin(BaseUserAdmin):
    inlines = [ProfilMembreInline]


# Réenregistrer l'admin User avec le profil inline
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(ProfilMembre)
class ProfilMembreAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'role', 'telephone', 'date_inscription')
    list_filter = ('role',)
    search_fields = ('utilisateur__username', 'utilisateur__email', 'utilisateur__first_name')
    readonly_fields = ('date_inscription',)
