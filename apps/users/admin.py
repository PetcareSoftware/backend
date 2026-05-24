from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role, ClinicalStaff, Veterinarian, Receptionist, Manager

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'role')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'phone_number', 'address')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Roles y extras', {'fields': ('role', 'profile_image_url')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Role)
admin.site.register(ClinicalStaff)
admin.site.register(Veterinarian)
admin.site.register(Receptionist)
admin.site.register(Manager)