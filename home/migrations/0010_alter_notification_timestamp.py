# Generated by Django 4.1.7 on 2023-04-22 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_remove_episode_img_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='timestamp',
            field=models.DateTimeField(auto_created=True, blank=True, null=True),
        ),
    ]