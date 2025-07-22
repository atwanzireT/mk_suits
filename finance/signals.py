from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Revenue
from django.utils import timezone
from decimal import Decimal
from inventory.models import OrderTransaction
from room_bookings.models import RoomReservation, Sauna_services
from otherPackages.models import OtherPackage
from .models import Budget, BudgetLine
from django.db.models.signals import pre_save, post_save

# Temporary storage to track changes
_previous_payment_modes = {}


@receiver(pre_save, sender=OrderTransaction)
def track_previous_payment_mode(sender, instance, **kwargs):
    if instance.pk:
        old_instance = OrderTransaction.objects.get(pk=instance.pk)
        _previous_payment_modes[instance.pk] = old_instance.payment_mode


@receiver(post_save, sender=OrderTransaction)
def create_revenue_from_order(sender, instance, created, **kwargs):
    excluded_modes = ["NO PAYMENT", "ON ACCOMMODATION", "INVOICE"]
    allowed_modes = ["CASH", "MOMO PAY", "AIRTEL PAY"]

    if created:
        return  # Don't act on creation because it's always "NO PAYMENT"

    previous_mode = _previous_payment_modes.get(instance.pk)

    # Only trigger if payment_mode changed and new mode is allowed
    if previous_mode != instance.payment_mode and instance.payment_mode in allowed_modes:
        if not Revenue.objects.filter(description__icontains=f"Order {instance.random_id}").exists():
            total_amount = sum(
                item.total_price for item in instance.order_items.all())

            Revenue.objects.create(
                category='fnb',
                description=f"F&B Payment for Order {instance.random_id}",
                amount=Decimal(total_amount),
                received_from=instance.customer_name or "walk-in",
                date=timezone.now().date(),
                created_by=instance.created_by,
            )

    # Clean up
    _previous_payment_modes.pop(instance.pk, None)

@receiver(post_save, sender=RoomReservation)
def add_revenue_on_check_in(sender, instance, created, **kwargs):
    if instance.status != "Pending" and instance.status != "Cancelled":
        # Prevent duplicate revenue entries
        description = f"Room {instance.room.room_number} check-in - {instance.reservation_id}"
        if not Revenue.objects.filter(description=description).exists():
            Revenue.objects.create(
                category='rooms',
                description=description,
                amount=instance.total_price,
                received_from=instance.customer or "Guest",
                date=timezone.now().date(),
                created_by=instance.created_by,
            )


@receiver(post_save, sender=OtherPackage)
def add_revenue_on_service_completion(sender, instance, created, **kwargs):
    if created:
        description = f"{instance.get_service_type_display()} - {instance.client_name} - {instance.id} - Initial Payment"
        Revenue.objects.create(
            category='other',
            description=description,
            amount=instance.amount_paid,
            received_from=instance.client_name,
            date=timezone.now().date(),
            created_by=instance.created_by,
        )


@receiver(post_save, sender=Revenue)
def update_budget_line_actual(sender, instance, created, **kwargs):
    if not created:
        return

    revenue_date = instance.date or timezone.now().date()
    month = revenue_date.month
    year = revenue_date.year

    from calendar import monthrange
    from datetime import date

    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    # Get or create budget
    budget, _ = Budget.objects.get_or_create(
        month=month,
        year=year,
        defaults={
            'revenue_estimate': 0,
            'expense_estimate': 0,
            'start_date': first_day,
            'end_date': last_day
        }
    )

    # Get or create budget line
    line, _ = BudgetLine.objects.get_or_create(
        budget=budget,
        category=instance.category,
        defaults={'estimated_amount': 0, 'actual_amount': 0}
    )

    # Update actual amount
    line.actual_amount += instance.amount
    line.save()
