from django.db import migrations, models
import django.db.models.deletion


def backfill_waiting_queue_fields(apps, schema_editor):
    WaitingListEntry = apps.get_model('appointments', 'WaitingListEntry')
    for entry in WaitingListEntry.objects.select_related('appointment__slot').all():
        entry.vet_id = entry.appointment.vet_id
        entry.queue_date = entry.appointment.slot.date
        entry.save(update_fields=['vet', 'queue_date'])


class Migration(migrations.Migration):
    dependencies = [
        ('appointments', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='waitinglistentry',
            name='vet',
            field=models.ForeignKey(
                db_column='vet_id',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='waiting_list_entries',
                to='users.veterinarian',
            ),
        ),
        migrations.AddField(
            model_name='waitinglistentry',
            name='queue_date',
            field=models.DateField(null=True),
        ),
        migrations.RunPython(backfill_waiting_queue_fields, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='waitinglistentry',
            name='vet',
            field=models.ForeignKey(
                db_column='vet_id',
                on_delete=django.db.models.deletion.PROTECT,
                related_name='waiting_list_entries',
                to='users.veterinarian',
            ),
        ),
        migrations.AlterField(
            model_name='waitinglistentry',
            name='queue_date',
            field=models.DateField(),
        ),
        migrations.RemoveConstraint(
            model_name='waitinglistentry',
            name='unique_waiting_position_per_appointment',
        ),
        migrations.AddConstraint(
            model_name='waitinglistentry',
            constraint=models.UniqueConstraint(fields=('vet', 'queue_date', 'position'), name='unique_waiting_position_per_vet_date'),
        ),
        migrations.AddIndex(
            model_name='waitinglistentry',
            index=models.Index(fields=['vet', 'queue_date', 'called_at'], name='waiting_vet_date_call_idx'),
        ),
    ]
