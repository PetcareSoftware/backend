import uuid
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('pets','0001_initial'), ('schedules','0001_initial')]
    operations = [
        migrations.CreateModel(name='Appointment', fields=[('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ('reason', models.CharField(max_length=500)), ('status', models.CharField(choices=[('SCHEDULED','Agendada'),('CONFIRMED','Confirmada'),('CHECKED_IN','Paciente llegó'),('COMPLETED','Completada'),('CANCELLED','Cancelada')], default='SCHEDULED', max_length=15)), ('notes', models.TextField(blank=True, null=True)), ('scheduled_at', models.DateTimeField()), ('cancelled_at', models.DateTimeField(blank=True, null=True)), ('cancellation_reason', models.TextField(blank=True, null=True)), ('created_at', models.DateTimeField(auto_now_add=True)), ('pet', models.ForeignKey(db_column='patient_id', on_delete=django.db.models.deletion.PROTECT, related_name='appointments', to='pets.pet')), ('slot', models.ForeignKey(db_column='slot_id', on_delete=django.db.models.deletion.PROTECT, related_name='appointments', to='schedules.timeslot')), ('vet', models.ForeignKey(db_column='vet_id', on_delete=django.db.models.deletion.PROTECT, related_name='appointments', to='users.veterinarian'))], options={'db_table':'appointments', 'ordering':['-scheduled_at']}),
        migrations.CreateModel(name='WaitingListEntry', fields=[('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ('position', models.IntegerField()), ('arrived_at', models.DateTimeField(auto_now_add=True)), ('called_at', models.DateTimeField(blank=True, null=True)), ('appointment', models.OneToOneField(db_column='appointment_id', on_delete=django.db.models.deletion.CASCADE, related_name='waiting_entry', to='appointments.appointment'))], options={'db_table':'waiting_list_entries','ordering':['arrived_at']}),
        migrations.AddConstraint(model_name='appointment', constraint=models.UniqueConstraint(condition=models.Q(('status__in', ['SCHEDULED','CONFIRMED','CHECKED_IN'])), fields=('slot',), name='unique_active_appointment_per_slot')),
        migrations.AddConstraint(model_name='appointment', constraint=models.UniqueConstraint(condition=models.Q(('status__in', ['SCHEDULED','CONFIRMED','CHECKED_IN'])), fields=('pet','slot'), name='unique_active_pet_appointment_per_slot')),
        migrations.AddConstraint(model_name='waitinglistentry', constraint=models.UniqueConstraint(fields=('appointment','position'), name='unique_waiting_position_per_appointment')),
    ]
