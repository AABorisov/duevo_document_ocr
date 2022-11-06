import os
from datetime import datetime
from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill

from document_processing import constants
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import time


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    password = models.CharField(verbose_name=_('Password'), max_length=128, null=True, default=None)
    email = models.EmailField(verbose_name=_("Email"), max_length=150, unique=True)
    first_name = models.CharField(_('first name'), max_length=30, null=True)
    last_name = models.CharField(_('last name'), max_length=150, null=True)
    gender = models.SmallIntegerField(verbose_name=_("Gender"), choices=constants.GENDER_CHOICES, default=0)

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/%Y/%m/%d/', null=True, blank=True)
    image_thumbnail = ImageSpecField(source='image',
                                      processors=[ResizeToFill(300, 300)],
                                      format='JPEG',
                                      options={'quality': 60})
    birthday = models.DateField(verbose_name=_("Birthday"), null=True, blank=True)
    job_title = models.CharField(verbose_name=_("Job title"), max_length=150, db_index=True, null=True, blank=True)
    phone = models.CharField(verbose_name=_("Phone"), max_length=20, db_index=True, null=True, blank=True)
    company_name = models.CharField(verbose_name=_("Company name"), max_length=150, db_index=True, null=True, blank=True)
    linkedin = models.CharField(verbose_name=_("Linkedin"), max_length=255, db_index=True, null=True, blank=True)
    facebook = models.CharField(verbose_name=_("Facebook"), max_length=255, db_index=True, null=True, blank=True)
    vkontakte = models.CharField(verbose_name=_("Vkontakte"), max_length=255, db_index=True, null=True, blank=True)
    instagram = models.CharField(verbose_name=_("Instagram"), max_length=255, db_index=True, null=True, blank=True)
    notes = models.TextField(verbose_name=_("Notes"), max_length=1000, null=True, blank=True)
    email_notify = models.SmallIntegerField(verbose_name=_("Email notify"), choices=constants.EMAIL_NOTIFY_CHOICES, default=0)

    def __str__(self):
        return f'{self.user.email} Profile'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    print(created)
    print(instance)
    if created:
        Token.objects.create(user=instance)

