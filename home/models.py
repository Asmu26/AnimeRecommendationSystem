from django.db import models
from django.contrib.auth.models import User
# Create your models here.
#For anime Data
class Animedata(models.Model):
    title = models.TextField()
    synopsis = models.TextField()
    genre = models.TextField()
    aired = models.TextField()
    episodes = models.IntegerField()
    popularity = models.IntegerField()
    ranked = models.IntegerField()
    score = models.FloatField()
    img_url =models.TextField()
    link = models.TextField()
    
class Episode(models.Model):
    anime=models.ForeignKey(Animedata,related_name='episode_of',on_delete=models.CASCADE)
    episode = models.IntegerField()
    episode_number =models.IntegerField()
    episode_name = models.TextField(max_length=500)
    synopsis = models.TextField()
    aired = models.TextField()
    img_url =models.TextField()

    
class WatchList(models.Model):
    class StatusChoices(models.TextChoices):
        COMPLETED = '0', 'Completed'
        DROPPED = '1', 'Dropped'
        PLAN_TO_WATCH = '2', 'Plan to Watch'
        ON_HOLD = '3', 'On Hold'
        WATCHING = '4', 'Watching'
    user = models.ForeignKey(User,related_name='added_by',on_delete=models.CASCADE)
    anime=models.ForeignKey(Animedata,related_name='added_to',on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=StatusChoices.choices)

class Notification(models.Model):
    title = models.TextField(max_length=255)
    anime=models.ForeignKey(Animedata,related_name='notification_of',on_delete=models.CASCADE)
    description = models.TextField(max_length=5000)


class NotificationView(models.Model):
    notification = models.ForeignKey(Notification, related_name='view_of', on_delete=models.CASCADE)
    user = models.ForeignKey(User,related_name='to',on_delete=models.CASCADE)
    is_viewed = models.BooleanField(default=False)