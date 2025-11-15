from django.db import models
from django.contrib.auth.models import User

class UserPreference(models.Model):
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=255, blank=True, null=True)
    monthly_budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='auto')

    def __str__(self):
        return f"{self.user}'s preferences"
