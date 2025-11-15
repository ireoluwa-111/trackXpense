from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import json
from django.http import JsonResponse
from django.db.models import Sum, Max
from datetime import datetime
from expenses.models import Expense


def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user
        ) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user
        ) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user
        ) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user
        )
        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'income/index.html', context)


@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/add_income.html', context)

        UserIncome.objects.create(
            owner=request.user,
            amount=amount,
            date=date,
            source=source,
            description=description
        )
        messages.success(request, 'Record saved successfully')

        return redirect('income')


@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/edit_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/edit_income.html', context)
        income.amount = amount
        income.date = date
        income.source = source
        income.description = description

        income.save()
        messages.success(request, 'Record updated successfully')

        return redirect('income')


def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'record removed')
    return redirect('income')


@login_required(login_url='/authentication/login')
def income_summary(request):
    income = UserIncome.objects.filter(owner=request.user)
    currency = UserPreference.objects.get(user=request.user).currency

    total_income = income.aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = Expense.objects.filter(owner=request.user).aggregate(total=Sum('amount'))['total'] or 0
    net_income = total_income - total_expenses

    latest_income = income.aggregate(latest=Max('date'))['latest']
    top_source = (
        income.values('source')
        .annotate(total=Sum('amount'))
        .order_by('-total')
        .first()
    )

    top_source_name = top_source['source'] if top_source else 'N/A'
    top_source_amount = top_source['total'] if top_source else 0

    monthly_summary = (
        income.values('date__year', 'date__month')
        .annotate(total=Sum('amount'))
        .order_by('-date__year', '-date__month')
    )

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_income': net_income,
        'latest_income': latest_income,
        'top_source_name': top_source_name,
        'top_source_amount': top_source_amount,
        'currency': currency,
        'monthly_summary': monthly_summary,
    }
    return render(request, 'income/income_summary.html', context)
