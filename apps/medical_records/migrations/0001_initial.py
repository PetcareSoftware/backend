import uuid
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('pets', '0001_initial'), ('users', '0001_initial')]
    operations = [
        migrations.CreateModel(name='MedicalRecord', fields=[('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ('created_at', models.DateTimeField(auto_now_add=True)), ('patient', models.OneToOneField(db_column='patient_id', on_delete=django.db.models.deletion.PROTECT, related_name='medical_record', to='pets.pet'))], options={'db_table':'medical_records'}),
    ]
