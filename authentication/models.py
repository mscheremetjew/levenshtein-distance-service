"""Models for users."""
import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import IntegrityError, models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Override BaseUserManager."""

    use_in_migrations = True

    def create_superuser(self, email, password, **extra_fields):
        """Create superuser."""
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password"""
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Extends the standard base user class with the type field.
    """

    email_validator = UnicodeUsernameValidator()

    email = models.EmailField(
        _("email address"),
        max_length=150,
        unique=True,
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        validators=[email_validator],
        error_messages={
            "unique": _("A user with that email address already exists."),
        },
    )
    username = models.CharField(
        _("username"),
        max_length=150,
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates that this user is a staff member and can access a limited view " "of Django Admin."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. " "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    # EMAIL_FIELD = 'email'
    USERNAME_FIELD = "email"

    def save(self, *args, **kwargs):
        """Create random username on save."""
        if not self.username:
            self.username = str(uuid.uuid4())
            for unused in range(10):
                try:
                    super().save(*args, **kwargs)
                    break
                except IntegrityError:
                    self.username = str(uuid.uuid4())
            else:
                raise unique_key_exception  # noqa
        else:
            super().save(*args, **kwargs)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
