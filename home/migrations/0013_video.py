# Generated by Django 4.1.7 on 2023-05-10 08:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_animerating'),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('episode_number', models.IntegerField()),
                ('title', models.CharField(max_length=255)),
                ('video_url', models.URLField()),
                ('anime', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='home.animedata')),
            ],
        ),
    ]