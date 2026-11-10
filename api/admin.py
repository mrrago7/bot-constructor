from django.contrib import admin

from .models import Bot, Scenario, Step
from .models import Bot, Scenario, Step, Conversation

admin.site.register(Conversation)
admin.site.register(Bot)
admin.site.register(Scenario)
admin.site.register(Step)
