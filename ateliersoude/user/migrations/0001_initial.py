# Generated by Django 2.2 on 2019-04-29 16:15

from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, verbose_name='last name')),
                ('street_address', models.CharField(default='', max_length=255, verbose_name='street address')),
                ('phone_number', models.CharField(blank=True, default='-', max_length=10, verbose_name='phone number')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='date of birth')),
                ('gender', models.CharField(blank=True, choices=[('m', 'Male'), ('f', 'Female'), ('n', 'Other')], default='n', max_length=1)),
                ('avatar_img', models.ImageField(blank=True, null=True, upload_to='media/avatar/', verbose_name='Avatar')),
                ('bio', models.TextField(blank=True, default='-', verbose_name='bio')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=100, verbose_name='Organization name')),
                ('description', models.TextField(default='', verbose_name='Activity description')),
                ('picture', models.ImageField(blank=True, null=True, upload_to='organizations/', verbose_name='Image')),
                ('active', models.BooleanField(verbose_name='Active')),
                ('slug', models.SlugField(default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('admins', models.ManyToManyField(blank=True, related_name='admin_organisations', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(blank=True, related_name='member_organisations', to=settings.AUTH_USER_MODEL)),
                ('visitors', models.ManyToManyField(blank=True, related_name='visitor_organisations', to=settings.AUTH_USER_MODEL)),
                ('volunteers', models.ManyToManyField(blank=True, related_name='volunteer_organisations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
