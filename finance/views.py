
from decimal import Decimal
from django.shortcuts import render, redirect
from .forms import RevenueForm, ExpenseForm, AssetForm, LiabilityForm
from django.contrib.auth.decorators import login_required
from datetime import datetime, date
from calendar import monthrange
from django.contrib import messages
from django.core.paginator import Paginator

from finance.models import Asset, Expense, Liability, Revenue
from django.db.models import Sum

# Create your views here.

# Financial Documents


def get_income_statement(start_date, end_date):
    total_revenue = Revenue.objects.filter(date__range=(
        start_date, end_date)).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = Expense.objects.filter(date__range=(
        start_date, end_date)).aggregate(Sum('amount'))['amount__sum'] or 0
    net_profit = total_revenue - total_expenses
    return {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
    }


def get_balance_sheet():
    total_assets = Asset.objects.aggregate(Sum('value'))['value__sum'] or 0
    total_liabilities = Liability.objects.aggregate(Sum('amount'))[
        'amount__sum'] or 0
    equity = total_assets - total_liabilities
    return {
        'assets': total_assets,
        'liabilities': total_liabilities,
        'equity': equity
    }


@login_required(login_url='/user/login/')
def financial_report(request):
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    income = get_income_statement(start_date, end_date)
    balance = get_balance_sheet()
    
    total_revenue = income.get('total_revenue', 0)


    net_profit = income.get('net_profit', 0)

    profit_margin = 0
    if total_revenue > 0:
        profit_margin = (net_profit / total_revenue) * 100

    assets = balance.get('assets', 0)
    liabilities = balance.get('liabilities', 0)

    debt_ratio = 0
    if assets > 0:
        debt_ratio = (liabilities / assets) * 100

    # Check if there’s any data to show
    has_data = any([
        income.get('total_revenue', 0),
        income.get('total_expenses', 0),
        income.get('net_profit', 0),
        balance  # you can refine this check further if needed
    ])

    if not has_data:
        messages.error(
            request, f"No financial data found for {start_date.strftime('%B %Y')}.")

    # Recommendations
    recommendations = []

    if income.get('net_profit', 0) < 0:
        recommendations = [
            "Consider reviewing your expenses to identify potential cost-saving opportunities.",
            "Explore strategies to increase revenue through new products or services."
        ]
    elif income.get('total_expenses', 0) > (income.get('total_revenue', 0) * Decimal('0.7')):
        recommendations = [
            "Your expenses are relatively high compared to revenue. Consider reviewing your cost structure."
        ]
    else:
        recommendations = [
            "Your business is performing well. Consider reinvesting profits into growth opportunities."
        ]

    context = {
        'income': income,
        'balance': balance,
        'profit_margin': profit_margin,
        'debt_ratio': debt_ratio,
        'start_date': start_date,
        'end_date': end_date,
        'recommendations': recommendations,
        'selected_year': year,
        'selected_month': month
    }

    return render(request, 'financial_summary.html', context)


@login_required(login_url='/user/login/')
def add_revenue(request):
    form = RevenueForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('finances')  # Update this if you have a list view
    return render(request, 'add_revenue.html', {'form': form})


@login_required(login_url='/user/login/')
def add_expense(request):
    form = ExpenseForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('finances')
    return render(request, 'add_expense.html', {'form': form})


@login_required(login_url='/user/login/')
def add_asset(request):
    form = AssetForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('finances')
    return render(request, 'add_asset.html', {'form': form})


@login_required(login_url='/user/login/')
def add_liability(request):
    form = LiabilityForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('finances')
    return render(request, 'add_liability.html', {'form': form})


@login_required(login_url='/user/login/')
def all_assets(request):
    assets_list = Asset.objects.all()

    return render(request, "assets.html", {"assets_list": assets_list})


@login_required(login_url='/user/login/')
def liabities(request):
    all_liability = Liability.objects.all()

    return render(request, "liability.html", {"all_liability": all_liability})



@login_required(login_url='/user/login/')
def revenue(request):
 
    revenue_list = Revenue.objects.all().order_by('-date')
    paginator = Paginator(revenue_list, 10)

    # Get the page number from the request
    page_number = request.GET.get('page')

    # Get the corresponding page
    sauna_list = paginator.get_page(page_number)

    return render(request, "revenue.html", {"revenue_list": revenue_list})





@login_required(login_url='/user/login/')
def all_expense(request):

    expense_list = Expense.objects.all().order_by('-date')
    paginator = Paginator(expense_list, 10)

    # Get the page number from the request
    page_number = request.GET.get('page')

    # Get the corresponding page
    expense_list = paginator.get_page(page_number)

    return render(request, "expense.html", {"expense_list": expense_list})
