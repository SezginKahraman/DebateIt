from django.contrib import admin

from .models import Room, Team, Participant, Judge, Break
from django.utils.safestring import mark_safe


admin.site.register(Room)
admin.site.register(Team)
admin.site.register(Participant)
admin.site.register(Judge)
admin.site.register(Break)
