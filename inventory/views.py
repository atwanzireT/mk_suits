import json
from datetime import datetime, timedelta

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from .models import OrderItem

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from core.models import Setting
from .forms import *
from .models import *
from django.shortcuts import render, get_object_or_404
from .models import OrderItem

# Global today's date in correct timezone
today = timezone.localdate()


# === DASHBOARD ===
@login_required(login_url='/user/login/')
def dashboard(request):
    start_of_today = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end_of_today = timezone.make_aware(datetime.combine(today + timedelta(days=1), datetime.min.time()))

    orderTodayCount = OrderItem.objects.filter(order_date__range=(start_of_today, end_of_today)).count()
    orderCount = OrderItem.objects.count()
    today_total_amount = OrderItem.objects.filter(order_date__range=(start_of_today, end_of_today)).aggregate(total=Sum('total_price'))['total'] or 0
    orders = OrderItem.objects.select_related('menu_item').order_by('-order_date')[:5]

    return render(request, "dashboard.html", {
        "orderTodayCount": orderTodayCount,
        "orderCount": orderCount,
        "orders": orders,
        "today_total_amount": today_total_amount,
    })


# === MENU ===
def load_menu_items(request):
    search_term = request.GET.get('term', '')  # optional: for search
    menu_items = MenuItem.objects.filter(
        name__icontains=search_term).values('id', 'name')[:10]
    return JsonResponse(list(menu_items), safe=False)


def search_menu_items(request):
    query = request.GET.get("q", "")
    results = MenuItem.objects.filter(name__icontains=query)[:20]
    data = [{"id": item.id, "name": item.name} for item in results]
    return JsonResponse(data, safe=False)




# === ORDERS ===
@login_required(login_url='/user/login/')
def orders(request):
    # Set the time range
    now_time = timezone.now()
    filter_time = now_time - timedelta(hours=12)

    # Query orders
    all_orders_count = OrderItem.objects.count()
    recent_orders = OrderItem.objects.filter(
        order_date__gte=filter_time
    ).select_related('order', 'table', 'dining_area').order_by('-order_date')
    recent_orders_count = recent_orders.count()

    # Debug output
    print(f"DEBUG - All orders: {all_orders_count}, Recent orders: {recent_orders_count}")
    print(f"DEBUG - Current time: {now_time}, Filter cutoff: {filter_time}")

    # Paginate the results
    paginator = Paginator(recent_orders, 10)
    page_number = request.GET.get('page')
    orders_list = paginator.get_page(page_number)

    return render(request, "order_list.html", {
        "orders_list": orders_list,
        "all_orders_count": all_orders_count,
        "recent_orders_count": recent_orders_count,
        "current_time": now_time,
        "filter_time": filter_time,
    })


@login_required(login_url='/user/login/')
def order_transaction_payment(request, order_id):
    order = get_object_or_404(OrderTransaction, id=order_id)

    if request.method == 'POST':
        order.payment_mode = request.POST.get('payment_mode')
        order.transaction_id = request.POST.get('transaction_id')
        order.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)


@login_required(login_url='/user/login/')
def add_order(request):
    today = localdate()
    # unpaid_orders = OrderTransaction.objects.all()
    unpaid_orders = OrderTransaction.objects.filter(
        created=today, payment_mode="NO PAYMENT").order_by('-id')
    # last_transaction_order = unpaid_orders.first()  # Get the latest unpaid order

    menu_items = MenuItem.objects.all().values('id', 'name', 'price')
    if request.method == 'POST':
        form = OrderTransactionForm(request.POST)
        if form.is_valid():
            order_transaction = form.save(commit=False)
            order_transaction.created_by = request.user
            order_transaction.save()
            # Ensure 'add_order' is a valid URL name.
            return redirect('add_order')
    else:
        form = OrderTransactionForm()

    return render(request, 'add_order.html', {
        'form': form,

        'all_menu_items': menu_items,
        # 'last_transaction_order': last_transaction_order,
        'unpaid_orders': unpaid_orders,
    })


@csrf_exempt
@login_required(login_url='/user/login/')
def submit_orders(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            order_id = data.get("random_id")
            customer_name = data.get("customer_name")
            order_type = data.get("order_type")
            status = data.get("status")
            special_notes = data.get("special_notes")
            orders = data.get("orders", [])

            if not orders:
                return JsonResponse({"error": "No menu items selected"}, status=400)

            # Fetch the order transaction
            try:
                order_transaction = OrderTransaction.objects.get(
                    random_id=order_id)
            except OrderTransaction.DoesNotExist:
                return JsonResponse({"error": "Order transaction not found"}, status=404)

            # Create multiple order items
            for order in orders:
                try:
                    menu_item = MenuItem.objects.get(id=order["menu_item_id"])
                    OrderItem.objects.create(
                        order=order_transaction,
                        menu_item=menu_item,
                        customer_name=customer_name,
                        quantity=order["quantity"],
                        status=status,
                        special_notes=special_notes,
                        order_type=order_type
                    )
                except MenuItem.DoesNotExist:
                    return JsonResponse({"error": f"Menu item with ID {order['menu_item_id']} not found"}, status=404)

            # Return JSON response with redirect URL
            return JsonResponse({"message": "Orders placed successfully!", "redirect_url": "/manager/orders_transactions/"})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


# === ORDER MANAGEMENT ===
@login_required
def getOrder(request, id):
    order = get_object_or_404(OrderItem, id=id)
    settings = Setting.objects.first()
    return render(request, "getorder.html", {"order": order, "setting": settings})


@login_required
def edit_order(request, id):
    order = get_object_or_404(OrderItem, id=id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('order_list')
    else:
        form = OrderForm(instance=order)
    return render(request, 'edit_order.html', {'form': form})


@login_required
def delete_order(request, id):
    order = get_object_or_404(OrderItem, id=id)
    if request.method == 'POST':
        order.delete()
        return redirect('orders')
    return render(request, 'delete_order.html', {'order': order})


# === ORDER TRANSACTIONS ===
@login_required
def orderTransactions(request):
    orders_list = OrderTransaction.objects.filter(payment_mode="NO PAYMENT").order_by('-updated', '-id')
    page = request.GET.get('page')
    orders_page = Paginator(orders_list, 10).get_page(page)
    return render(request, "ordertransactions.html", {"orders_list": orders_page})


@login_required
def clearedTransactions(request):
    orders_list = OrderTransaction.objects.filter(payment_mode__in=["CASH", "MOMO PAY", "AIRTEL PAY"]).order_by('-id')
    page = request.GET.get('page')
    orders_page = Paginator(orders_list, 10).get_page(page)
    return render(request, "cleared_order_transactions.html", {"orders_list": orders_page})


@login_required
def getOrderTransaction(request, id):
    order = get_object_or_404(OrderTransaction, id=id)
    settings = Setting.objects.first()
    order_items = OrderItem.objects.filter(order=order).exclude(status='Cancelled')
    total_price = sum(item.total_price for item in order_items)

    return render(request, "getordertransactions.html", {
        'order': order,
        'order_items': order_items,
        'total_price': total_price,
        'setting': settings
    })


# === REPORTS & CHARTS ===
@login_required
def monthly_order_totals(request):
    data = (
        OrderTransaction.objects
        .annotate(month=TruncMonth('created'))
        .values('month')
        .annotate(total_orders=Count('id'))
        .order_by('month')
    )

    return JsonResponse({
        'months': [item['month'].strftime('%b') for item in data],
        'totals': [item['total_orders'] for item in data]
    })


@login_required
def pos_reports(request):
    return render(request, "reports.html", {})



@require_POST
def update_order_status(request, order_id):
    try:
        order = get_object_or_404(OrderItem, pk=order_id)
        status = request.POST.get("status")

        if status not in dict(OrderItem._meta.get_field("status").choices):
            return JsonResponse({"error": "Invalid status"}, status=400)

        order.status = status
        order.save()
        return JsonResponse({"message": "Order status updated successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


