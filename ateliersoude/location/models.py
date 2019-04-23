from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from ateliersoude.user.models import CustomUser, Organization
from ateliersoude.utils import validate_image


class Place(models.Model):
    name = models.CharField(
        max_length=100, null=False, blank=False, verbose_name=_("Name")
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=False
    )
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    description = models.TextField(
        null=False,
        blank=False,
        default="",
        verbose_name=_("Place description"),
    )
    place_type = models.CharField(max_length=100, default="Other")
    slug = models.SlugField(default="", blank=True)
    address = models.CharField(
        max_length=255, verbose_name=_("street address")
    )
    longitude = models.FloatField()
    latitude = models.FloatField()
    picture = models.ImageField(
        upload_to="places/",
        blank=True,
        null=True,
        validators=[validate_image],
        verbose_name=_("Image"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("location:place_detail", args=(self.pk, self.slug))

    def __str__(self):
        return self.name
