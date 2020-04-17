from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from allauth.utils import generate_unique_username

from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            **kwargs
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.active = True
        user.save()
        return user


class User(AbstractUser):

    # Set `email` as the username field and remove it from
    # Django's default REQUIRED_FIELDS definition.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    TYPE_VENDOR = 'vendor'
    TYPE_CUSTOMER = 'customer'
    USER_TYPES_CHOICES = (
        (TYPE_VENDOR, 'Vendor'),
        (TYPE_CUSTOMER, 'Customer'),
    )
    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_("Name of User"), blank=True, null=True, max_length=255)
    email = models.EmailField(_('email address'), unique=True)
    address = models.CharField(max_length=200, blank=True)
    # Only `Vendor` users should have unique numbers and require to input.
    phone_number = PhoneNumberField(null=True, blank=True, unique=True,
        help_text='Phone number used for 2FA Authentication.',
    )
    business_name = models.CharField(max_length=100, blank=True)
    user_type =  models.CharField(choices=USER_TYPES_CHOICES, max_length=20,
                    default=TYPE_CUSTOMER)
    authy_id = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        help_text='Authentication ID from Twilio 2FA API.',
    )

    objects = UserManager()


    def save(self, *args, **kwargs):
        """Custom save to autosave `username` field."""
        if not self.id:
            self.username = generate_unique_username([
                self.name,
                self.email,
                self.Meta.verbose_name
            ])
        return super(User, self).save(*args, **kwargs)

    @property
    def is_phone_verified(self):
        return True if self.authy_id else False

    @property
    def is_customer(self):
        return self.user_type == self.TYPE_CUSTOMER

    @property
    def is_vendor(self):
        return self.user_type == self.TYPE_VENDOR

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
