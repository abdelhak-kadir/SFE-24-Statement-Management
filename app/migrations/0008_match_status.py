# Generated by Django 5.0.4 on 2024-05-23 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_match'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
