from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Animedata, Episode, WatchList, Notification,UserProfile,NotificationAudit

# @receiver(post_save, sender=Animedata)
@receiver(post_save, sender=Episode)
def send_notification(sender, instance, created, **kwargs):
    if instance:
        if sender == Animedata:
            anime = instance
        elif sender == Episode:
            anime = instance.anime
            
        watchlists = WatchList.objects.filter(anime=anime, status__in=['completed','plan_to_watch','on_hold','watching'])
        for watchlist in watchlists:
            title=f"New episode of {anime.title} is now available!",
            description=f"Episode {instance.episode_number} of {anime.title} has been released."
            notification = Notification.objects.create(title=title,anime=anime,description=description)
            notification_audit = NotificationAudit.objects.create(title=title,anime=anime,description=description)
            user_profile = UserProfile.objects.get(user=watchlist.user)
            user_profile.notifications.add(notification)
            user_profile.notification_audits.add(notification_audit)

post_save.connect(send_notification, sender=Episode)