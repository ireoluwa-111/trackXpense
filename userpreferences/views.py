from django.shortcuts import render
import os
import json
from django.conf import settings
from .models import UserPreference
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

@login_required
def account_settings(request):
    user = request.user
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            user.email = email
            user.save()
            messages.success(request, 'Email updated successfully')
    return render(request, 'preferences/account.html')


def index(request):
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for k, v in data.items():
            currency_data.append({'name': k, 'value': v})

    user_preferences, created = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        currency = request.POST.get('currency')
        monthly_budget = request.POST.get('monthly_budget')
        theme = request.POST.get('theme')

        user_preferences.currency = currency
        user_preferences.monthly_budget = monthly_budget or None
        user_preferences.theme = theme
        user_preferences.save()

        messages.success(request, 'Preferences updated successfully')

    context = {
        'currencies': currency_data,
        'user_preferences': user_preferences,
    }

    return render(request, 'preferences/index.html', context)

@login_required
def account_settings(request):
    user = request.user
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            user.email = email
            user.save()
            messages.success(request, 'Email updated successfully')
    return render(request, 'preferences/account.html')
