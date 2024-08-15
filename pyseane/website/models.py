from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid


class Pyseane_UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(password=password, **extra_fields)


class Pyseane_User(AbstractUser):
    # Ajoutez vos champs supplémentaires ici
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    # Ajoutez d'autres champs selon vos besoins

    REQUIRED_FIELDS = ['email']

    objects = Pyseane_UserManager()

    def __str__(self):
        return self.username


class campagne_fish(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(Pyseane_User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100, null=True)
    url = models.CharField(null=True)

    def __str__(self):
        return self.nom


class target(models.Model):
    id_email_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    campagne = models.ForeignKey(campagne_fish, on_delete=models.CASCADE)
    has_read = models.BooleanField(default=False)
    has_open = models.BooleanField(default=False)
    has_logged = models.BooleanField(default=False)

    def __str__(self):
        return self.nom
