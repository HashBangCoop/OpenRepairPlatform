from django.db import models


class Condition(models.Model):
    name = models.CharField(
        verbose_name=_("Condition Type"),
        max_length=100,
        null=False,
        blank=False,
        default="",
    )
    resume = models.CharField(
        verbose_name=_("Condition resume"),
        max_length=100,
        null=False,
        blank=False,
        default="",
    )
    description = models.TextField(
        verbose_name=_("Condition description"),
        null=False, blank=False, default="")
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True)
    price = models.IntegerField(
        verbose_name=_("Price"), null=False, blank=True, default=5
    )

    def __str__(self):
        return self.name


# EventType is an activity
class Activity(models.Model):
    name = models.CharField(
        verbose_name=_("Activity type"),
        max_length=100,
        null=False,
        blank=False,
        default="",
    )
    slug = models.SlugField(default="", unique=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True)
    description = models.TextField(
        verbose_name=_("Activity description"),
        null=False, blank=False, default="")
    picture = models.ImageField(
        verbose_name=_("Image"),
        upload_to="activities/")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("activity_detail", args=(self.pk, self.slug))


# ------------------------------------------------------------------------------


class Event(models.Model):
    title = models.CharField(
        verbose_name=_("Title"),
        max_length=150,
        null=True,
        blank=True,
        default="")
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=False)
    condition = models.ManyToManyField(
        Condition,
        related_name="condition_activity",
        verbose_name=_("Conditions"),
        blank=True,
    )
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    published = models.BooleanField(
        verbose_name=_("Published"), null=False, default=False
    )
    publish_at = models.DateTimeField(
        verbose_name=_("Publication date and time"),
        null=False,
        blank=False,
        default=timezone.now,
    )
    type = models.ForeignKey(Activity, on_delete=models.DO_NOTHING)
    slug = models.SlugField(default="", unique=True)
    starts_at = models.DateTimeField(
        verbose_name=_("Start date and time"),
        null=False,
        blank=False,
        default=timezone.now,
    )
    ends_at = models.DateTimeField(
        verbose_name=_("End date and time"),
        null=False,
        blank=False,
        default=timezone.now,
    )
    available_seats = models.IntegerField(
        verbose_name=_("Available seats"), null=False, blank=True, default=0
    )
    attendees = models.ManyToManyField(
        CustomUser,
        related_name="attendee_user",
        verbose_name=_("Attendees"),
        blank=True,
    )
    presents = models.ManyToManyField(
        CustomUser,
        related_name="present_user",
        verbose_name=_("Presents"),
        blank=True)
    organizers = models.ManyToManyField(
        CustomUser,
        related_name="organizer_user",
        verbose_name=_("Organizers"),
        blank=True,
    )
    location = models.ForeignKey(Place, on_delete=models.DO_NOTHING, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super().save(*args, kwargs)

    def date_interval_format(self):
        starts_at_date = self.starts_at.date().strftime("%A %d %B %Y")
        starts_at_time = self.starts_at.time().strftime("%X")
        ends_at_time = self.ends_at.time().strftime("%X")

        # ex Lundi 01 Janvier 2018 de 20:01:12 à 22:01:12
        string = starts_at_date
        string += " de "
        string += starts_at_time
        string += " à "
        string += ends_at_time
        return string

    def get_absolute_url(self):
        return reverse("event_detail", args=(self.pk, self.slug))

    def __str__(self):
        full_title = "%s %s" % (
            self.title,
            self.starts_at.date().strftime("%A %d %B %Y"),
        )
        return full_title


class PublishedEventManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(published=True)
            .filter(publish_at__lte=timezone.now())
        )


class PublishedEvent(Event):
    objects = PublishedEventManager()

    class Meta:
        proxy = True


# ------------------------------------------------------------------------------
