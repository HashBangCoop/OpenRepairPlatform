from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from ateliersoude.user.models import CustomUser, Organization


class PlaceType(models.Model):
    name = models.CharField(
        max_length=100, verbose_name=_("Type"), null=False, blank=False
    )
    slug = models.SlugField(unique=True, default="")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.slug

    @classmethod
    def get_other_place(cls):
        return Place.objects.get_or_create(name="Other")[0]


class Place(models.Model):
    name = models.CharField(
        max_length=100, null=False, blank=False, verbose_name=_("Name")
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=False
    )
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    description = models.TextField(
        verbose_name=_("Place description"),
        null=False,
        blank=False,
        default="",
    )

    type = models.ForeignKey(
        PlaceType,
        verbose_name=_("Type"),
        null=False,
        on_delete=models.SET(PlaceType.get_other_place),
    )

    slug = models.SlugField(default="", unique=True)
    # geolocation is provided by the AddressField
    address = models.CharField(
        verbose_name=_("street address"),
        max_length=255,
        blank=True,
        default="",
    )
    picture = models.ImageField(verbose_name=_("Image"), upload_to="places/")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("place_detail", args=(self.pk, self.slug))

    def __str__(self):
        return self.name
