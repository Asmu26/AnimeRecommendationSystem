# Generated by Django 4.1.7 on 2023-05-12 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0013_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='animedata',
            name='average_rating',
            field=models.FloatField(default=0.0),
        ),
    ]