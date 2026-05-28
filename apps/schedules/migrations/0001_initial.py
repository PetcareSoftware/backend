import uuid
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('users', '0001_initial')]
    operations = [
        migrations.CreateModel(name='VetSchedule', fields=[('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ('day_of_week', models.SmallIntegerField()), ('start_time', models.TimeField()), ('end_time', models.TimeField()), ('slot_duration_min', models.IntegerField(default=30)), ('is_active', models.BooleanField(default=True)), ('vet', models.ForeignKey(db_column='vet_id', on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='users.veterinarian'))], options={'db_table':'vet_schedules'}),
        migrations.CreateModel(name='TimeSlot', fields=[('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ('date', models.DateField()), ('start_time', models.TimeField()), ('end_time', models.TimeField()), ('status', models.CharField(choices=[('FREE','Libre'),('BOOKED','Reservado'),('BLOCKED','Bloqueado')], default='FREE', max_length=10)), ('vet', models.ForeignKey(db_column='vet_id', on_delete=django.db.models.deletion.CASCADE, related_name='time_slots', to='users.veterinarian'))], options={'db_table':'time_slots', 'ordering':['date','start_time']}),
        migrations.AddConstraint(model_name='vetschedule', constraint=models.CheckConstraint(condition=models.Q(('day_of_week__gte', 0), ('day_of_week__lte', 6)), name='schedule_day_of_week_0_6')),
        migrations.AddConstraint(model_name='vetschedule', constraint=models.CheckConstraint(condition=models.Q(('slot_duration_min__gt', 0)), name='schedule_duration_positive')),
        migrations.AddConstraint(model_name='timeslot', constraint=models.UniqueConstraint(fields=('vet','date','start_time','end_time'), name='unique_timeslot_per_vet_date_time')),
    ]
