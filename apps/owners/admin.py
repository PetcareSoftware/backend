from django.contrib import admin
from .models import Owner

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'dni', 'phone')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'dni')
