# assets/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime

from room_bookings.models import Room
from .models import RoomAsset, MonthlyAudit, AuditItem, Asset, AssetCategory


@login_required
def dashboard(request):
    """Asset Management Dashboard"""
    total_assets = RoomAsset.objects.count()
    assets_needing_maintenance = RoomAsset.objects.filter(status='maintenance').count()
    pending_audits = MonthlyAudit.objects.filter(completed=False).count()
    
    context = {
        'total_assets': total_assets,
        'assets_needing_maintenance': assets_needing_maintenance,
        'pending_audits': pending_audits,
    }
    return render(request, 'assets/dashboard.html', context)

@login_required
def room_assets_list(request, room_id=None):
    """List assets for a specific room or all rooms"""
    if room_id:
        room = get_object_or_404(Room, id=room_id)
        room_assets = RoomAsset.objects.filter(room=room).select_related('asset')
        context = {
            'room': room,
            'room_assets': room_assets,
            'single_room_view': True,
        }
    else:
        rooms_with_assets = Room.objects.filter(room_assets__isnull=False).distinct()
        context = {
            'rooms': rooms_with_assets,
            'single_room_view': False,
        }
    
    return render(request, 'assets/room_assets_list.html', context)

@login_required
def monthly_audits(request):
    """List monthly audits"""
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    audits = MonthlyAudit.objects.filter(
        audit_date__month=current_month,
        audit_date__year=current_year
    ).select_related('room', 'auditor')
    
    context = {
        'audits': audits,
        'current_month': datetime.now().strftime('%B %Y'),
    }
    return render(request, 'assets/monthly_audits.html', context)

@login_required
def audit_detail(request, audit_id):
    """Detail view for a specific audit"""
    audit = get_object_or_404(MonthlyAudit, id=audit_id)
    audit_items = AuditItem.objects.filter(audit=audit).select_related('room_asset__asset')
    
    if request.method == 'POST':
        # Mark audit as completed
        audit.completed = True
        audit.save()
        messages.success(request, 'Audit marked as completed!')
        return redirect('assets:monthly_audits')
    
    context = {
        'audit': audit,
        'audit_items': audit_items,
    }
    return render(request, 'assets/audit_detail.html', context)