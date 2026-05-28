"""
Modelos locales de identidad para Backend 1.

ADVERTENCIA DE INTEGRACIÓN:
Módulo 5 / Seguridad también participa en la identidad del sistema. Estas
tablas existen aquí para sostener el ERD, las llaves foráneas internas y
AUTH_USER_MODEL de Django. Antes de integrar bases de datos, confirmar con
Módulo 5 si `users` y `roles` serán espejo local sincronizado, tablas
compartidas o si Backend 1 debe migrar a referencias UUID planas.
Ver docs/REPORTE_EQUIPO_POSTGRES_MODULO5.md.
"""
import uuid
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from apps.common.roles import ROLE_CHOICES, OWNER, MANAGER


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'roles'
        ordering = ['name']

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role=OWNER, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio.')
        email = self.normalize_email(email)
        role_obj, _ = Role.objects.get_or_create(name=role)
        user = self.model(email=email, role=role_obj, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        return self.create_user(email=email, password=password, role=MANAGER, is_active=True, **extra_fields)


class User(AbstractBaseUser):
    # AbstractBaseUser aporta hash/validación de contraseña; db_column mantiene ERD: password_hash.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField('password', max_length=255, db_column='password_hash')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.ForeignKey(Role, db_column='role_id', on_delete=models.PROTECT, related_name='users')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = UserManager()

    class Meta:
        db_table = 'users'
        ordering = ['email']

    @property
    def role_name(self):
        return self.role.name if self.role_id else None

    @property
    def is_staff(self):
        return self.role_name == MANAGER

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

    def __str__(self):
        return self.email


class ClinicalStaff(models.Model):
    user = models.OneToOneField(User, primary_key=True, db_column='user_id', on_delete=models.CASCADE, related_name='clinical_staff')
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    hire_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'clinical_staff'

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'.strip() or self.user.email


class Veterinarian(models.Model):
    user = models.OneToOneField(ClinicalStaff, primary_key=True, db_column='user_id', on_delete=models.CASCADE, related_name='veterinarian')
    license_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    specialty = models.CharField(max_length=100, null=True, blank=True)
    max_appts_per_day = models.IntegerField(default=8)

    class Meta:
        db_table = 'veterinarians'

    @property
    def account(self):
        return self.user.user

    @property
    def full_name(self):
        account = self.account
        return f'{account.first_name} {account.last_name}'.strip() or account.email

    def __str__(self):
        return self.full_name
