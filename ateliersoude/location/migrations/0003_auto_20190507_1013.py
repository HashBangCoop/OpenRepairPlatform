# Generated by Django 2.2 on 2019-05-07 08:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0002_place_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='user.Organization'),
        ),
    ]
