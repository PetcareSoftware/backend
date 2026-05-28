from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('vaccinations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vaccinationevent',
            name='sync_status',
            field=models.CharField(
                choices=[('SYNCED', 'Sincronizado'), ('PENDING_SYNC', 'Pendiente de sincronización')],
                default='SYNCED',
                max_length=20,
            ),
        ),
    ]
