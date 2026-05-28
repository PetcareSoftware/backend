from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('user', models.OneToOneField(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='owner_profile', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('phone', models.CharField(blank=True, max_length=30, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('dni', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('emergency_contact', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={'db_table': 'owners'},
        ),
    ]
