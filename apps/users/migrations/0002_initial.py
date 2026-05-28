# Generado por Django 5.2.14 el 2026-05-18 16:43

from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        # Se asume que el nombre del archivo de la migración anterior también se pasó a inglés
        ('users', '0001_create_receptionist_permissions'), 
    ]

    operations = [
        migrations.CreateModel(
            name='Supply',  # 'Insumo' en inglés para el código y la base de datos
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='nombre')),  # Código en inglés, visualización en español
                ('current_stock', models.IntegerField(default=0, verbose_name='stock actual')),
            ],
            options={
                # Esto asegura que en el panel de administración de Django se siga leyendo en español
                'verbose_name': 'insumo',
                'verbose_name_plural': 'insumos',
            },
        ),
    ]