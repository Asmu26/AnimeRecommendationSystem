from django.contrib import admin
from .models import Animedata,UserProfile,Episode
# Register your models here.
#Recommendation data
class AnimedataAdmin(admin.ModelAdmin):
    list_display = ('title',  'genre', 'aired', 'episodes', 'score')
    list_filter = ('genre', 'aired')
    search_fields = ('title', 'synopsis')

class UserProfileAdmin(admin.ModelAdmin):
    fields =['user','notifications']
class EpisodeAdmin(admin.ModelAdmin):
    fields = ['anime','episode_number','episode_name' ,'synopsis','aired']

admin.site.register(Animedata, AnimedataAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Episode, EpisodeAdmin)