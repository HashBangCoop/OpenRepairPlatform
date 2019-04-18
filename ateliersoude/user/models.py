import logging

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class CustomUserManager(BaseUserManager):
    def _create_user(
        self, email, password, is_staff, is_superuser, **extra_fields
    ):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDER_MALE = "m"
    GENDER_FEMALE = "f"
    GENDER_OTHER = "o"
    GENDERS = (
        (GENDER_MALE, _("Male")),
        (GENDER_FEMALE, _("Female")),
        (GENDER_OTHER, _("Other")),
    )
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """
    email = models.EmailField(_("email address"), max_length=254, unique=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin " "site."
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

    street_address = models.CharField(
        verbose_name=_("street address"),
        max_length=255,
        blank=True,
        default="",
    )

    phone_number = models.CharField(
        _("phone number"), max_length=15, blank=True, null=True
    )

    birth_date = models.DateField(_("date of birth"), blank=True, null=True)

    # TODO maybe better put an explicit value and set a default, like 'n'
    gender = models.CharField(
        max_length=1, choices=GENDERS, blank=True, default=GENDER_OTHER
    )

    avatar_img = models.ImageField(
        verbose_name=_("Avatar"),
        upload_to="media/avatar/",
        null=True,
        blank=True,
    )
    bio = models.TextField(_("bio"), blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("user")

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name

    def get_absolute_url(self):
        return reverse("user:user_detail", kwargs={"pk": self.pk})

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def __str__(self):
        if self.first_name or self.last_name:
            full_name = "%s %s" % (self.first_name, self.last_name)
            return full_name.strip()
        else:
            return self.email


class Organization(models.Model):
    name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name=_("Organization name"),
    )
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    description = models.TextField(
        verbose_name=_("Activity description"),
        null=False,
        blank=False,
        default="",
    )
    picture = models.ImageField(
        verbose_name=_("Image"), upload_to="organizations/", null=True
    )
    active = models.BooleanField(verbose_name=_("Active"))
    slug = models.SlugField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("user:organization_detail", args=(self.pk, self.slug))


class OrganizationPerson(models.Model):
    VISITOR = 0
    MEMBER = 10
    VOLUNTEER = 20
    ADMIN = 30
    MEMBER_TYPES = (
        (VISITOR, _("Visitor")),
        (MEMBER, _("Member")),
        (VOLUNTEER, _("Volunteer")),
        (ADMIN, _("Admin")),
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True
    )
    role = models.SmallIntegerField(choices=MEMBER_TYPES, default=VISITOR)

    class Meta:
        unique_together = ("organization", "user", "role")


# --- visitor ---
class OrganizationVisitorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=OrganizationPerson.VISITOR)


class OrganizationVisitor(OrganizationPerson):
    objects = OrganizationVisitorManager()

    class Meta:
        proxy = True


# --- member ---
class OrganizationMemberManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=OrganizationPerson.MEMBER)


class OrganizationMember(OrganizationPerson):
    objects = OrganizationMemberManager()

    class Meta:
        proxy = True


# --- volunteer ---
class Abilities(models.Model):
    name = models.CharField(
        max_length=100, null=False, blank=False, verbose_name=_("Abilities")
    )


class OrganizationVolunteerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=OrganizationPerson.VOLUNTEER)


class OrganizationVolunteer(OrganizationPerson):
    abilities = models.ManyToManyField(Abilities)
    tagline = models.TextField(verbose_name=_("Tagline"))
    objects = OrganizationVolunteerManager()


# --- admin ---
class OrganizationAdminstratorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=OrganizationPerson.ADMIN)


class OrganizationAdministrator(OrganizationPerson):
    objects = OrganizationAdminstratorManager()

    class Meta:
        proxy = True


# extend the Organization with convenience methods


def get_admins(self):
    queryset = OrganizationPerson.objects.filter(
        role=OrganizationPerson.ADMIN, organization=self
    )
    ret = []
    for query in queryset:
        ret += [query.user]
    return ret


def get_volunteers(self):
    queryset = OrganizationPerson.objects.filter(
        role=OrganizationPerson.VOLUNTEER, organization=self
    )
    ret = []
    for query in queryset:
        ret += [query.user]
    return ret


def get_members(self):
    queryset = OrganizationPerson.objects.filter(
        role=OrganizationPerson.MEMBER, organization=self
    )
    ret = []
    for query in queryset:
        ret += [query.user]
    return ret


def get_visitors(self):
    queryset = OrganizationPerson.objects.filter(
        role=OrganizationPerson.VISITOR, organization=self
    )
    ret = []
    for query in queryset:
        ret += [query.user]
    return ret


Organization.admins = get_admins
Organization.visitors = get_visitors
Organization.members = get_members
Organization.volunteers = get_volunteers
