from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail


class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError(_("L'utilisateur doit avoir une adresse e-mail"))
        if not full_name:
            raise ValueError(_("L'utilisateur doit avoir un nom complet"))
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Le superutilisateur doit avoir 'is_staff=True'"))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Le superutilisateur doit avoir 'is_superuser=True'"))

        return self.create_user(email, full_name, password, **extra_fields)

# user
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("adresse e-mail"), unique=True, max_length=255)
    full_name = models.CharField(_("nom complet"), max_length=255, blank=False)
    is_active = models.BooleanField(_("actif"), default=True)
    is_staff = models.BooleanField(_("membre du personnel"), default=False)
    is_superuser = models.BooleanField(_("superutilisateur"), default=False)
    email_verified = models.BooleanField(_("email vérifié"), default=False)
    created_at = models.DateTimeField(_("date de création"), auto_now_add=True)
    updated_at = models.DateTimeField(_("date de mise à jour"), auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    class Meta:
        verbose_name = _("utilisateur")
        verbose_name_plural = _("utilisateurs")

    def __str__(self):
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def verify_email(self):
        self.email_verified = True
        self.save(update_fields=['email_verified'])

    def reset_password(self, new_password):
        self.set_password(new_password)
        self.save(update_fields=['password'])

    def staff_type(self):
        if hasattr(self, 'inspecteur_profile'):
            return "inspecteur"
        elif hasattr(self, 'formateur_profile'):
            return "formateur"
        elif hasattr(self, 'participant_profile'):
            return "participant"
        else:
            return None




class Inspecteur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='inspecteur_profile')
    specialisation = models.CharField(max_length=100, verbose_name="Spécialisation")
    zone_inspection = models.CharField(max_length=100, verbose_name="Zone d'inspection")

    def __str__(self):
        return f"{self.user.full_name} - Inspecteur"


class Formateur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='formateur_profile')
    expertise = models.CharField(max_length=255, verbose_name="Domaine d'expertise")
    years_experience = models.PositiveIntegerField(verbose_name="Années d'expérience")

    def __str__(self):
        return f"{self.user.full_name} - Formateur"


