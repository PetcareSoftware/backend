from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        if 'username' not in extra_fields or not extra_fields.get('username'):
            extra_fields['username'] = email
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    # permissions eliminado
    def __str__(self):
        return self.name

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    # phone_number y address eliminados (se mueven a Owner)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    profile_image_url = models.URLField(max_length=500, blank=True, null=True)
    is_phone_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = UserManager()
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

class ClinicalStaff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='clinical_staff')
    phone = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dni = models.CharField(max_length=20, blank=True, null=True)
    hired_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Staff - {self.user.email}"

class Veterinarian(models.Model):
    clinical_staff = models.OneToOneField(ClinicalStaff, on_delete=models.CASCADE, related_name='veterinarian')
    specialty = models.CharField(max_length=100, blank=True, null=True)
    # license_number omitido según líder

    def __str__(self):
        return f"Veterinarian - {self.clinical_staff.user.email}"



