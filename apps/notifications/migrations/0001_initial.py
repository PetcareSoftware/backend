import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name='Notification', fields=[('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ('title', models.CharField(max_length=150)), ('message', models.TextField()), ('notification_type', models.CharField(choices=[('REMINDER','Recordatorio de cita'),('CONFIRMATION','Confirmación de asistencia'),('ALERT','Alerta'),('STATUS_CHANGE','Cambio de estado'),('GENERAL','General')], default='GENERAL', max_length=50)), ('is_read', models.BooleanField(default=False)), ('created_at', models.DateTimeField(auto_now_add=True)), ('read_at', models.DateTimeField(blank=True, null=True)), ('user', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL))], options={'db_table':'notifications','ordering':['-created_at']}),
        migrations.CreateModel(name='NotificationLog', fields=[('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ('channel', models.CharField(max_length=50)), ('status', models.CharField(choices=[('SENT','Enviada'),('FAILED','Fallida'),('PENDING','Pendiente')], default='PENDING', max_length=20)), ('detail', models.TextField(blank=True, null=True)), ('appointment_id', models.UUIDField(blank=True, null=True)), ('created_at', models.DateTimeField(auto_now_add=True)), ('notification', models.ForeignKey(blank=True, db_column='notification_id', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='notifications.notification'))], options={'db_table':'notification_logs'}),
    ]
