from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

# Register your models here.


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('tipo_cuenta', 'rol_personal')}),
    )
    list_display = ('username', 'email', 'tipo_cuenta', 'rol_personal', 'is_staff')
