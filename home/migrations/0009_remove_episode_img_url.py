# Generated by Django 4.1.7 on 2023-04-22 10:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_remove_episode_episode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='episode',
            name='img_url',
        ),
    ]