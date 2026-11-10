from django.db import models
from django.contrib.auth.models import User

class Bot(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Scenario(models.Model):
    bot = models.OneToOneField(Bot, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    data = models.JSONField(default=dict)


class Step(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    prompt = models.TextField()
    next_step = models.ForeignKey("self",on_delete=models.SET_NULL, null=True, blank=True)

class Conversation(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    current_step = models.ForeignKey(
        Step,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)