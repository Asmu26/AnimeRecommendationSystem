from django.db import models
from django.contrib.auth.models import User 
from django.contrib.auth.models import AbstractUser, Group, Permission
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
    average_rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.title

    def calculate_average_rating(self):
        ratings = self.ratings.all()
        if ratings.count() > 0:
            total_ratings = sum([rating.rating for rating in ratings])
            return total_ratings / ratings.count()
        else:
            return 0.0

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
        COMPLETED = 'completed', 'Completed'
        DROPPED = 'dropped', 'Dropped'
        PLAN_TO_WATCH = 'plan_to_watch', 'Plan to Watch'
        ON_HOLD = 'on_hold', 'On Hold'
        WATCHING = 'watching', 'Watching'
    
    user = models.ForeignKey(User, related_name='added_by', on_delete=models.CASCADE)
    anime = models.ForeignKey(Animedata, related_name='added_to', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=StatusChoices.choices)

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

    def save(self, *args, **kwargs):
        super(AnimeRating, self).save(*args, **kwargs)
        self.anime.average_rating = self.anime.calculate_average_rating()
        self.anime.save()

class Video(models.Model):
    anime = models.ForeignKey(Animedata, on_delete=models.CASCADE, related_name='videos')
    episode_number = models.IntegerField()
    title = models.CharField(max_length=255)
    video_url = models.URLField()

    def __str__(self):
        return f"{self.anime.title} - Episode {self.episode_number}"

