from django.conf import settings
from django.db import models
from django.db.models import Sum
from datetime import date

class Revenue(models.Model):
    REVENUE_CHOICES = [
        ('rooms', 'Rooms'),
        ('fnb', 'Food & Beverage'),
        ('party', 'Party'),
        ('other', 'Other')
    ]
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=100, blank=True, null=True, choices=REVENUE_CHOICES) 
    attachment = models.FileField(upload_to='attachments/%Y/%m/%d/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    received_from = models.CharField(max_length=30, default="staff")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='+')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='+')
    def __str__(self):
        return f"Revenue: {self.description} - {self.amount}"

class Expense(models.Model):
    EXPENCE_CHOICES = [
        ('staff', 'Salaries and Wages'),
        ('utilities', 'Utilities'),
        ('repairs', 'Repairs and Maintenance'),
        ('supplies', 'Cleaning & Room Supplies'),
        ('fnb', 'Food and Beverage'),
        ('admin', 'Administrative'),
        ('marketing', 'Sales and Marketing'),
        ('finance', 'Finance Costs'),
        ('depreciation', 'Depreciation'),
        ('other', 'Other'),
        ('other_pack','Other_Packages')

    ]
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=100, blank=True, null=True,  choices=EXPENCE_CHOICES)
    attachment = models.FileField(upload_to='attachments/%Y/%m/%d/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='+')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='+')
    def __str__(self):
        return f"Expense: {self.description} - {self.amount}"


class Asset(models.Model):
    name = models.CharField(max_length=255)
    value = models.DecimalField(
        max_digits=12, decimal_places=2)  # Original value
    purchase_date = models.DateField(null=True, blank=True)
    life_years = models.PositiveIntegerField(null=True, blank=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    attachment = models.FileField(
        upload_to='attachments/%Y/%m/%d/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    def depreciation_per_year(self):
        if self.life_years and self.value:
            return self.value / self.life_years
        return 0

    def years_elapsed(self):
        if self.purchase_date:
            return max(0, date.today().year - self.purchase_date.year)
        return 0

    def total_depreciation(self):
        return min(self.depreciation_per_year() * self.years_elapsed(), self.value)

    def current_value(self):
        return max(self.value - self.total_depreciation(), 0)

    @property
    def depreciation_amount(self):
        return self.total_depreciation()

    def __str__(self):
        return f"{self.name} - Current Value: {self.current_value()}"


class Liability(models.Model):
    class LiabilityCategory(models.TextChoices):
        LOAN = 'LOAN', "Loan / Debt"
        PAYABLE = 'PAYABLE', "Accounts Payable"
        OTHER = 'OTHER', "Other"

    description = models.CharField(
        max_length=255, verbose_name="Liability Description")
    category = models.CharField(max_length=50, choices=LiabilityCategory.choices,
                                default=LiabilityCategory.OTHER, verbose_name="Liability Category")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    date_received = models.DateField(null=True, blank=True)
    remaining_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00)
    due_date = models.DateField(blank=True, null=True)
    attachment = models.FileField(
        upload_to="attachments/liability/", blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name="liabilities_created", editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name="liabilities_updated", editable=False)
    is_active = models.BooleanField(default=True, verbose_name="Active")

    def save(self, *args, **kwargs):
        if not self.remaining_balance:
            self.remaining_balance = self.amount
        super().save(*args, **kwargs)

    @property
    def is_paid(self):
        return self.remaining_balance <= 0

    @property
    def days_overdue(self):
        if self.is_active and self.due_date and not self.is_paid:
            today = date.today()
            if today > self.due_date:
                return (today - self.due_date).days
        return 0

    @property
    def amount_paid(self):
        return self.payments.aggregate(total=Sum('amount_paid'))['total'] or 0
    def __str__(self):
        return f"{self.description} - UGX {self.amount}"

    class Meta:
        verbose_name = "Liability"
        verbose_name_plural = "Liabilities"
        ordering = ["-due_date", "-id"]


class LiabilityPayment(models.Model):
    liability = models.ForeignKey(
        Liability, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    new_due_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='liability_payments')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update liability balance and optionally due date
        self.liability.remaining_balance -= self.amount_paid
        if self.new_due_date:
            self.liability.due_date = self.new_due_date
        self.liability.save()
class Budget(models.Model):
    MONTH_CHOICES = [(i, i) for i in range(1, 13)]

    month = models.PositiveIntegerField(choices=MONTH_CHOICES)
    year = models.PositiveIntegerField()
    revenue_estimate = models.DecimalField(max_digits=12, decimal_places=2)
    expense_estimate = models.DecimalField(max_digits=12, decimal_places=2)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('month', 'year')

    @property
    def actual_revenue_range(self):
        if self.start_date and self.end_date:
            return Revenue.objects.filter(
                date__range=(self.start_date, self.end_date)
            ).aggregate(total=Sum('amount'))['total'] or 0
        return 0

    @property
    def actual_expense_range(self):
        if self.start_date and self.end_date:
            return Expense.objects.filter(
                date__range=(self.start_date, self.end_date)
            ).aggregate(total=Sum('amount'))['total'] or 0
        return 0

    @property
    def revenue_variance(self):
        return self.actual_revenue_range - self.revenue_estimate

    @property
    def expense_variance(self):
        return self.expense_estimate - self.actual_expense_range

    def __str__(self):
        return f"Budget: {self.month}/{self.year}"


class BudgetLine(models.Model):
    CATEGORY_CHOICES = [
        ('fnb', 'F&B'),
        ('rooms', 'Room Bookings'),
        ('other', 'Other Packages'),
        ('expense', 'Expenses'),
    ]
    budget = models.ForeignKey(
        Budget, on_delete=models.CASCADE, related_name='lines')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    estimated_amount = models.DecimalField(max_digits=12, decimal_places=2)
    actual_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.get_category_display()} - {self.estimated_amount}"
