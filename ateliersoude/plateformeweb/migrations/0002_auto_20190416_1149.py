# Generated by Django 2.2 on 2019-04-16 09:49

import ateliersoude.plateformeweb.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('plateformeweb', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='place',
            name='type',
            field=models.ForeignKey(on_delete=models.SET(ateliersoude.plateformeweb.models.PlaceType.get_other_place), to='plateformeweb.PlaceType', verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='organizationperson',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plateformeweb.Organization'),
        ),
        migrations.AddField(
            model_name='organizationperson',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='organization',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='attendees',
            field=models.ManyToManyField(blank=True, related_name='attendee_user', to=settings.AUTH_USER_MODEL, verbose_name='Attendees'),
        ),
        migrations.AddField(
            model_name='event',
            name='condition',
            field=models.ManyToManyField(blank=True, related_name='condition_activity', to='plateformeweb.Condition', verbose_name='Conditions'),
        ),
        migrations.AddField(
            model_name='event',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='plateformeweb.Place'),
        ),
        migrations.AddField(
            model_name='event',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plateformeweb.Organization'),
        ),
        migrations.AddField(
            model_name='event',
            name='organizers',
            field=models.ManyToManyField(blank=True, related_name='organizer_user', to=settings.AUTH_USER_MODEL, verbose_name='Organizers'),
        ),
        migrations.AddField(
            model_name='event',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='presents',
            field=models.ManyToManyField(blank=True, related_name='present_user', to=settings.AUTH_USER_MODEL, verbose_name='Presents'),
        ),
        migrations.AddField(
            model_name='event',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='plateformeweb.Activity'),
        ),
        migrations.AddField(
            model_name='condition',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='plateformeweb.Organization'),
        ),
        migrations.AddField(
            model_name='activity',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='plateformeweb.Organization'),
        ),
        migrations.AddField(
            model_name='activity',
            name='participants',
            field=models.ManyToManyField(related_name='activities', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='OrganizationAdministrator',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('plateformeweb.organizationperson',),
        ),
        migrations.CreateModel(
            name='OrganizationMember',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('plateformeweb.organizationperson',),
        ),
        migrations.CreateModel(
            name='OrganizationVisitor',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('plateformeweb.organizationperson',),
        ),
        migrations.CreateModel(
            name='PublishedEvent',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('plateformeweb.event',),
        ),
        migrations.AddField(
            model_name='organizationvolunteer',
            name='abilities',
            field=models.ManyToManyField(to='plateformeweb.Abilities'),
        ),
        migrations.AlterUniqueTogether(
            name='organizationperson',
            unique_together={('organization', 'user', 'role')},
        ),
    ]
