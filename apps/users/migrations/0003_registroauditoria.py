# Generado por Django 5.2.14 el 2026-05-24 01:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',  # Nombre del modelo en inglés (RegistroAuditoria)
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=10, verbose_name='acción')),
                ('path', models.CharField(max_length=255, verbose_name='ruta')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='fecha')),
                ('details', models.TextField(blank=True, null=True, verbose_name='detalles')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='usuario')),
            ],
            options={
                # Configuración para que el panel de administración lo muestre en español
                'verbose_name': 'registro de auditoría',
                'verbose_name_plural': 'registros de auditoría',
            },
        ),
    ]