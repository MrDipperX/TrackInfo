from django.contrib import admin
from .models import PassengerTrack


class PassengerTrackAdmin(admin.ModelAdmin):
    list_display = ('number', )
    list_display_links = ('number', )


admin.site.register(PassengerTrack, PassengerTrackAdmin)
