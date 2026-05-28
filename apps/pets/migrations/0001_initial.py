import uuid
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('owners', '0001_initial')]
    operations = [
        migrations.CreateModel(name='Species', fields=[('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ('name', models.CharField(max_length=100, unique=True))], options={'db_table': 'species', 'ordering': ['name']}),
        migrations.CreateModel(name='Breed', fields=[('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ('name', models.CharField(max_length=100)), ('species', models.ForeignKey(db_column='species_id', on_delete=django.db.models.deletion.PROTECT, related_name='breeds', to='pets.species'))], options={'db_table': 'breeds', 'ordering': ['species__name', 'name']}),
        migrations.CreateModel(name='Pet', fields=[('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)), ('is_deleted', models.BooleanField(default=False)), ('name', models.CharField(max_length=100)), ('birth_date', models.DateField(blank=True, null=True)), ('sex', models.CharField(blank=True, choices=[('M','Macho'),('F','Hembra')], max_length=1, null=True)), ('weight_kg', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)), ('color', models.CharField(blank=True, max_length=100, null=True)), ('microchip_id', models.CharField(blank=True, max_length=100, null=True, unique=True)), ('breed', models.ForeignKey(db_column='breed_id', on_delete=django.db.models.deletion.PROTECT, related_name='pets', to='pets.breed')), ('owner', models.ForeignKey(db_column='owner_id', on_delete=django.db.models.deletion.PROTECT, related_name='pets', to='owners.owner'))], options={'db_table': 'patients', 'ordering': ['name']}),
        migrations.AddConstraint(model_name='breed', constraint=models.UniqueConstraint(fields=('species', 'name'), name='unique_breed_per_species')),
    ]
