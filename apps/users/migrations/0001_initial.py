# Generated for PetCare Backend 1 corrected package
import uuid
from django.db import migrations, models
import django.db.models.deletion


def create_roles(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    for name in ['OWNER', 'RECEPTIONIST', 'VET', 'TECH_VET', 'MANAGER']:
        Role.objects.get_or_create(name=name)


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(choices=[('OWNER','Propietario'),('RECEPTIONIST','Recepcionista'),('VET','Veterinario'),('TECH_VET','Técnico veterinario'),('MANAGER','Administrador/Gerente')], max_length=50, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'roles', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('password', models.CharField(db_column='password_hash', max_length=255, verbose_name='password')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('role', models.ForeignKey(db_column='role_id', on_delete=django.db.models.deletion.PROTECT, related_name='users', to='users.role')),
            ],
            options={'db_table': 'users', 'ordering': ['email']},
        ),
        migrations.CreateModel(
            name='ClinicalStaff',
            fields=[
                ('user', models.OneToOneField(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='clinical_staff', serialize=False, to='users.user')),
                ('employee_id', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('hire_date', models.DateField(blank=True, null=True)),
            ],
            options={'db_table': 'clinical_staff'},
        ),
        migrations.CreateModel(
            name='Veterinarian',
            fields=[
                ('user', models.OneToOneField(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='veterinarian', serialize=False, to='users.clinicalstaff')),
                ('license_number', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('specialty', models.CharField(blank=True, max_length=100, null=True)),
                ('max_appts_per_day', models.IntegerField(default=8)),
            ],
            options={'db_table': 'veterinarians'},
        ),
        migrations.RunPython(create_roles, migrations.RunPython.noop),
    ]
