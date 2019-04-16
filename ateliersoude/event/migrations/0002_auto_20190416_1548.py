# Generated by Django 2.2 on 2019-04-16 13:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("location", "0001_initial"),
        ("event", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="attendees",
            field=models.ManyToManyField(
                blank=True,
                related_name="attendee_user",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Attendees",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="condition",
            field=models.ManyToManyField(
                blank=True,
                related_name="condition_activity",
                to="event.Condition",
                verbose_name="Conditions",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="location",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="location.Place",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="organization",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="user.Organization",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="organizers",
            field=models.ManyToManyField(
                blank=True,
                related_name="organizer_user",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Organizers",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="owner",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="presents",
            field=models.ManyToManyField(
                blank=True,
                related_name="present_user",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Presents",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="event.Activity",
            ),
        ),
        migrations.AddField(
            model_name="condition",
            name="organization",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="user.Organization",
            ),
        ),
        migrations.AddField(
            model_name="activity",
            name="organization",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="user.Organization",
            ),
        ),
        migrations.CreateModel(
            name="PublishedEvent",
            fields=[],
            options={"proxy": True, "indexes": [], "constraints": []},
            bases=("event.event",),
        ),
    ]
