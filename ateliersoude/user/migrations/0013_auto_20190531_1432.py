# Generated by Django 2.2 on 2019-05-31 12:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_merge_20190531_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalorganization',
            name='advised_fee',
            field=models.PositiveIntegerField(blank=True, default=0, verbose_name='Advised contribution'),
        ),
        migrations.AlterField(
            model_name='historicalorganization',
            name='min_fee',
            field=models.PositiveIntegerField(blank=True, default=0, verbose_name='Minimum contribution'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='user.Organization'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='organization',
            name='advised_fee',
            field=models.PositiveIntegerField(blank=True, default=0, verbose_name='Advised contribution'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='min_fee',
            field=models.PositiveIntegerField(blank=True, default=0, verbose_name='Minimum contribution'),
        ),
    ]
