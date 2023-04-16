from django.contrib import admin
from .models import Animedata
# Register your models here.
#Recommendation data
class AnimedataAdmin(admin.ModelAdmin):
    list_display = ('title',  'genre', 'aired', 'episodes', 'score')
    list_filter = ('genre', 'aired')
    search_fields = ('title', 'synopsis')


admin.site.register(Animedata, AnimedataAdmin)