from .models import Budget, BudgetLine
from django.contrib import admin
from .models import Asset, Budget, Liability, Expense, Revenue, BudgetLine
@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'value', 'purchase_date', 'is_active'] 
    search_fields = ['name']
    list_filter = ['is_active', 'purchase_date'] 

@admin.register(Liability)
class LiabilityAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'due_date', 'is_active'] 
    search_fields = ['description']
    list_filter = ['is_active', 'due_date'] 

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['category', 'description', 'amount', 'date', 'is_active'] 
    search_fields = ['category', 'description']
    list_filter = ['category', 'is_active', 'date']

@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = ['category', 'description', 'amount', 'received_from', 'date', 'is_active']
    search_fields = ['category', 'received_from', 'description']
    list_filter = ['category', 'is_active', 'date']
    

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = [
        'month',
        'year',
        'revenue_estimate',
        'actual_revenue_total',
        'revenue_variance',
        'expense_estimate',
        'actual_expense_total',
        'expense_variance',
        'created_by',
        'created_at',
    ]
    list_filter = ['month', 'year']
    search_fields = ['created_by__username']
    ordering = ['-year', '-month']

    def actual_revenue_total(self, obj):
        return sum(line.estimated_amount for line in obj.lines.all() if line.category in ['fnb', 'rooms', 'other'])
    actual_revenue_total.short_description = 'Actual Revenue'

    def revenue_variance(self, obj):
        return self.actual_revenue_total(obj) - obj.revenue_estimate
    revenue_variance.short_description = 'Revenue Variance'

    def actual_expense_total(self, obj):
        return sum(line.estimated_amount for line in obj.lines.all() if line.category == 'expense')
    actual_expense_total.short_description = 'Actual Expense'

    def expense_variance(self, obj):
        return self.actual_expense_total(obj) - obj.expense_estimate
    expense_variance.short_description = 'Expense Variance'


@admin.register(BudgetLine)
class BudgetLineAdmin(admin.ModelAdmin):
    list_display = ['budget', 'category', 'actual_amount', 'estimated_amount']
    search_fields = ['budget__year', 'budget__month', 'category']
