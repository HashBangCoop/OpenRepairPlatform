import logging

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDER_MALE = "m"
    GENDER_FEMALE = "f"
    GENDER_OTHER = "n"
    GENDERS = (
        (GENDER_MALE, _("Male")),
        (GENDER_FEMALE, _("Female")),
        (GENDER_OTHER, _("Other")),
    )

    email = models.EmailField(_("email address"), max_length=254, unique=True)
    first_name = models.CharField(_("first name"), max_length=30, default="")
    last_name = models.CharField(_("last name"), max_length=30, default="")
    street_address = models.CharField(
        verbose_name=_("street address"), max_length=255, default="-"
    )
    phone_number = models.CharField(
        _("phone number"), max_length=10, blank=True, default="-"
    )
    birth_date = models.DateField(_("date of birth"), blank=True, null=True)
    gender = models.CharField(
        max_length=1, choices=GENDERS, blank=True, default=GENDER_OTHER
    )
    avatar_img = models.ImageField(
        verbose_name=_("Avatar"),
        upload_to="media/avatar/",
        null=True,
        blank=True,
    )
    bio = models.TextField(_("bio"), blank=True, default="-")

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."
        ),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as "
            "active. Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    @property
    def get_organizations(self):
        member_orgas, visitor_orgas, volunteer_orgas, admin_orgas = (
            self.member_organizations.all(),
            self.visitor_organizations.all(),
            self.volunteer_organizations.all(),
            self.admin_organizations.all(),
        )
        return member_orgas.union(visitor_orgas, volunteer_orgas, admin_orgas)

    def get_absolute_url(self):
        return reverse("user:user_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.email


class Organization(models.Model):
    name = models.CharField(
        max_length=100, default="", verbose_name=_("Organization name")
    )
    description = models.TextField(
        verbose_name=_("Activity description"), default=""
    )
    picture = models.ImageField(
        verbose_name=_("Image"),
        upload_to="organizations/",
        null=True,
        blank=True,
    )
    slug = models.SlugField(default="")
    visitors = models.ManyToManyField(
        CustomUser, related_name="visitor_organizations", blank=True
    )
    members = models.ManyToManyField(
        CustomUser, related_name="member_organizations", blank=True
    )
    volunteers = models.ManyToManyField(
        CustomUser, related_name="volunteer_organizations", blank=True
    )
    admins = models.ManyToManyField(
        CustomUser, related_name="admin_organizations", blank=True
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "user:organization_detail",
            kwargs={"pk": self.pk, "slug": self.slug},
        )

    def __str__(self):
        return self.name
