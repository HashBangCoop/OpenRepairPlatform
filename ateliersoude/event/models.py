import datetime

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from ateliersoude.location.models import Place
from ateliersoude.user.models import CustomUser, Organization
from ateliersoude.utils import get_future_published_events, validate_image


class Condition(models.Model):
    name = models.CharField(verbose_name=_("Condition Type"), max_length=100)
    description = models.TextField(verbose_name=_("Condition description"))
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="conditions"
    )
    price = models.FloatField(verbose_name=_("Price"), default=5)

    def get_absolute_url(self):
        return reverse(
            "user:organization_detail",
            kwargs={
                "pk": self.organization.pk,
                "slug": self.organization.slug,
            },
        )

    def __str__(self):
        return self.name


class Activity(models.Model):
    name = models.CharField(verbose_name=_("Activity type"), max_length=100)
    slug = models.SlugField(blank=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="activities"
    )
    description = models.TextField(verbose_name=_("Activity description"))
    picture = models.ImageField(
        verbose_name=_("Image"),
        upload_to="activities/",
        blank=True,
        null=True,
        validators=[validate_image],
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("event:activity_detail", args=(self.pk, self.slug))

    def next_events(self):
        return get_future_published_events(self.event_set)


class Event(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="events"
    )
    conditions = models.ManyToManyField(
        Condition,
        related_name="events",
        verbose_name=_("Conditions"),
        blank=True,
    )
    published = models.BooleanField(verbose_name=_("Published"), default=False)
    publish_at = models.DateTimeField(
        verbose_name=_("Publication date and time"), default=timezone.now
    )
    activity = models.ForeignKey(
        Activity, on_delete=models.SET_NULL, null=True
    )
    slug = models.SlugField(blank=True)
    starts_at = models.DateTimeField(
        verbose_name=_("Start date and time"), default=timezone.now
    )
    ends_at = models.DateTimeField(verbose_name=_("End date and time"))
    available_seats = models.IntegerField(
        verbose_name=_("Available seats"), default=0
    )
    registered = models.ManyToManyField(
        CustomUser,
        related_name="registered_events",
        verbose_name=_("Registered"),
        blank=True,
    )
    presents = models.ManyToManyField(
        CustomUser,
        related_name="presents_events",
        verbose_name=_("Presents"),
        blank=True,
    )
    organizers = models.ManyToManyField(
        CustomUser,
        related_name="organizers_events",
        verbose_name=_("Organizers"),
        blank=True,
    )
    location = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.activity.name)
        return super().save(*args, kwargs)

    @property
    def remaining_seats(self):
        return self.available_seats - self.registered.count()

    def date_interval_format(self):
        starts_at_date = self.starts_at.date().strftime("%A %d %B")
        starts_at_time = self.starts_at.time().strftime("%H:%M")
        ends_at_time = self.ends_at.time().strftime("%H:%M")

        # ex Lundi 01 Janvier 2018 de 20:01:12 à 22:01:12
        return f"{starts_at_date} de {starts_at_time} à {ends_at_time}"

    def get_absolute_url(self):
        return reverse("event:detail", args=(self.pk, self.slug))

    @property
    def has_ended(self):
        return self.ends_at + datetime.timedelta(hours=4) < timezone.now()

    @property
    def has_started(self):
        return self.starts_at - datetime.timedelta(hours=2) < timezone.now()

    @classmethod
    def future_published_events(cls):
        return get_future_published_events(cls.objects)

    def __str__(self):
        full_title = "%s du %s" % (
            self.activity.name,
            self.starts_at.date().strftime("%d %B"),
        )
        return full_title
