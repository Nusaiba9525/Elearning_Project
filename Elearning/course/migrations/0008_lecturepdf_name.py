# Generated by Django 5.1.3 on 2024-11-16 04:32

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0007_lecturepdf_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='lecturepdf',
            name='name',
            field=models.CharField(default=django.utils.timezone.now, max_length=255),
            preserve_default=False,
        ),
    ]
