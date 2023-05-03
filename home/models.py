from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    notifications = models.ManyToManyField('Notification', blank=True)
    notification_audits = models.ManyToManyField('NotificationAudit', blank=True)

    def add_notification(self, title, anime, description):
        notification = Notification.objects.create(
            title=title,
            anime=anime,
            description=description
        )
        self.notifications.add(notification)
    def add_notification_audits(self, title, anime, description):
        audit = NotificationAudit.objects.create(
            title=title,
            anime=anime,
            description=description
        )
        self.notification_audits.add(audit)

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
    def __str__(self):
        return self.user.username

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
    def __str__(self):
        return self.title
    
class Episode(models.Model):
    anime=models.ForeignKey(Animedata,related_name='episode_of',on_delete=models.CASCADE)
    # episode = models.IntegerField()
    episode_number =models.IntegerField()
    episode_name = models.TextField(max_length=500)
    synopsis = models.TextField()
    aired = models.TextField()
    # img_url =models.TextField()
    def __str__(self):
        return self.anime.title+' '+self.episode_name

    
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
    timestamp = models.DateTimeField(auto_created=True,null=True,blank=True)

class NotificationAudit(models.Model):
    title = models.TextField(max_length=255)
    anime=models.ForeignKey(Animedata,related_name='notificationaudit_of',on_delete=models.CASCADE)
    description = models.TextField(max_length=5000)
    timestamp = models.DateTimeField(auto_created=True,null=True,blank=True)


class NotificationView(models.Model):
    notification = models.ForeignKey(Notification, related_name='view_of', on_delete=models.CASCADE)
    user = models.ForeignKey(User,related_name='to',on_delete=models.CASCADE)
    is_viewed = models.BooleanField(default=False)



class AnimeRating(models.Model):
    anime = models.ForeignKey(Animedata, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='anime_ratings')
    rating = models.IntegerField()

    class Meta:
        unique_together = ('user', 'anime')

