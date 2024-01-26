# Generated by Django 4.2.6 on 2024-01-23 13:50

import apis.authentication.model_helpers
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordResetUrl',
            fields=[
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(db_index=True, default=apis.authentication.model_helpers.generate_password_reset_token_id, editable=False, max_length=60, primary_key=True, serialize=False, unique=True)),
                ('user_id', models.CharField(default='', max_length=70)),
                ('used', models.BooleanField(default=True)),
                ('token', models.CharField(db_index=True, default='', max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RefreshToken',
            fields=[
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(db_index=True, default=apis.authentication.model_helpers.generate_refresh_token_id, editable=False, max_length=60, primary_key=True, serialize=False, unique=True)),
                ('code', models.CharField(db_index=True, default='', max_length=70)),
                ('user_id', models.CharField(default='', max_length=70)),
                ('used', models.BooleanField(default=True)),
                ('expiry_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
