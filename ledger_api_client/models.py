from __future__ import unicode_literals

import os
import zlib

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
# from django.contrib.postgres.fields import JSONField
from django.db.models import JSONField
from django.db import models, IntegrityError, transaction
#from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.dispatch import receiver
from django.db.models import Q
from django.db.models.signals import post_delete, pre_save, post_save
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django_countries.fields import CountryField
from ledger_api_client import ledger_models
from ledger_api_client import managed_models
from datetime import datetime, date



class EmailUserManager(BaseUserManager):
    """A custom Manager for the EmailUser model.
    """
    use_in_migrations = True

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """Creates and saves an EmailUser with the given email and password.
        """
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email).lower()
        if EmailUser.objects.filter(email__iexact=email):
            raise ValueError('This email is already in use')
        user = self.model(
            email=email, is_staff=is_staff, is_superuser=is_superuser)
        user.extra_data = extra_fields
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


#class EmailUser(AbstractBaseUser):
class EmailUser(AbstractBaseUser, PermissionsMixin):
    """Custom authentication model for the ledger project.
    Password and email are required. Other fields are optional.
    """
    email = models.EmailField(unique=True, blank=False)
    ledger_id = models.IntegerField(null=True,blank=True) 
    first_name = models.CharField(max_length=128, blank=False, verbose_name='Given name(s)')
    last_name = models.CharField(max_length=128, blank=False)
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into the admin site.',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as active.'
                  'Unselect this instead of deleting ledger.accounts.',
    )
    date_joined = models.DateTimeField(default=timezone.now)

    TITLE_CHOICES = (
        ('Mr', 'Mr'),
        ('Miss', 'Miss'),
        ('Mrs', 'Mrs'),
        ('Ms', 'Ms'),
        ('Dr', 'Dr')
    )
    title = models.CharField(max_length=100, choices=TITLE_CHOICES, null=True, blank=True,
                             verbose_name='title', help_text='')
    ledger_groups = JSONField(default=dict)
    ledger_data = JSONField(default=dict)

    objects = EmailUserManager()
    USERNAME_FIELD = 'email'

    def save(self, *args, **kwargs):
        if not self.email:
            self.email = self.get_dummy_email()

        self.email = self.email.lower()
        super(EmailUser, self).save(*args, **kwargs)

    def get_full_name(self):
        full_name = '{} {}'.format(self.first_name, self.last_name)
        #.encode('utf-8').strip()
        return full_name



class DataStore(models.Model):
    key_name = models.CharField(max_length=100)
    data = JSONField(default=dict) 

    def __str__(self):
        return self.key_name

    class Meta:
        verbose_name = 'Data Store'
        verbose_name_plural = 'Data Stores'

