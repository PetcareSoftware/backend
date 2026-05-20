from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

def create_recepcionista_role(apps, schema_editor):
    User = get_user_model()
    content_type = ContentType.objects.get_for_model(User)

    permisos = [
        ('add_manual_appointment', 'Add Manual Appointment'),
        ('view_calendar_availability', 'View Calendar Availability'),
        ('register_attendance', 'Register Attendance'),
        ('manage_waitlist', 'Manage Waitlist'),
        ('view_appointment_history', 'View Appointment History'),
    ]

    perm_objects = []
    for codename, name in permisos:
        perm, created = Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type,
        )
        perm_objects.append(perm)

    group, created = Group.objects.get_or_create(name='recepcionista')
    group.permissions.add(*perm_objects)

class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),  # ← REEMPLAZA ESTO con la última migración de auth que anotaste
    ]
    operations = [
        migrations.RunPython(create_recepcionista_role),
    ]