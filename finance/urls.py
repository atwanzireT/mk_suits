from django.urls import path
from . import views

urlpatterns = [
    path('financial-report/', views.financial_report, name='finances'),
    path('revenue/add/', views.add_revenue, name='add_revenue'),
    path('expense/add/', views.add_expense, name='add_expense'),
    path('asset/add/', views.add_asset, name='add_asset'),
    path('liability/add/', views.add_liability, name='add_liability'),
    
    
    #lists
    path('all-assets/', views.all_assets, name='assets'),
    path('all-liabilities/', views.liabities, name='liabilities'),
    path('all-revenue/', views.revenue, name='revenue'),
    path('all-expense/', views.expense, name='expense'),
    path('asset-detail/<int:id>/', views.asset_detail, name='asset_detail'),
    path('register-depreciation/', views.register_depreciation,
         name='register_depreciation'),    
    
    
    #budget
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/create/', views.budget_create, name='budget_create'),
    path('budgets/<int:pk>/', views.budget_detail, name='budget_detail'),
    path('budgets/<int:budget_id>/add-line/',
         views.budget_line_create, name='budget_line_create'),
    
    
    #Unit costing
    path('unit/costing/', views.unit_costing_report, name='unit_cost')

    
]
