# assets/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q
from .models import RoomAsset, MonthlyAudit, AuditItem, Asset, AssetCategory, AssetMaintenanceLog
from room_bookings.models import Room
from .forms import AssetForm, RoomAssetForm, QuickRoomAssetForm, AssetCategoryForm, AssetMaintenanceForm

@login_required
def dashboard(request):
    """Asset Management Dashboard"""
    total_assets = RoomAsset.objects.count()
    assets_needing_maintenance = RoomAsset.objects.filter(status='maintenance').count()
    pending_audits = MonthlyAudit.objects.filter(completed=False).count()
    
    # Recent maintenance activities
    recent_maintenance = AssetMaintenanceLog.objects.select_related('room_asset__room', 'room_asset__asset').order_by('-maintenance_date')[:5]
    
    context = {
        'total_assets': total_assets,
        'assets_needing_maintenance': assets_needing_maintenance,
        'pending_audits': pending_audits,
        'recent_maintenance': recent_maintenance,
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
def add_room_asset(request, room_id=None):
    """Add asset to a room - with quick creation option"""
    initial = {}
    if room_id:
        room = get_object_or_404(Room, id=room_id)
        initial['room'] = room
    
    if request.method == 'POST':
        form = QuickRoomAssetForm(request.POST, initial=initial)
        if form.is_valid():
            # Handle asset creation or selection
            asset_name = request.POST.get('asset_name', '').strip()
            category_name = request.POST.get('category_name', '').strip()
            
            if asset_name:
                # Get or create category
                category = None
                if category_name:
                    category, created = AssetCategory.objects.get_or_create(
                        name=category_name,
                        defaults={'description': f'Category for {category_name}'}
                    )
                
                # Get or create asset
                asset, created = Asset.objects.get_or_create(
                    name=asset_name,
                    defaults={
                        'category': category,
                        'model': 'Standard',
                        'purchase_date': timezone.now().date(),
                    }
                )
                
                # Create room asset assignment
                room_asset = form.save(commit=False)
                room_asset.asset = asset
                room_asset.save()
                
                messages.success(request, f'Successfully added {asset_name} to room!')
                return redirect('assets:room_assets_detail', room_id=room_asset.room.id)
    else:
        form = QuickRoomAssetForm(initial=initial)
    
    # Get available rooms for dropdown
    rooms = Room.objects.all()
    
    context = {
        'form': form,
        'rooms': rooms,
        'room': room if room_id else None,
    }
    return render(request, 'assets/add_room_asset.html', context)

@login_required
def edit_room_asset(request, room_asset_id):
    """Edit existing room asset"""
    room_asset = get_object_or_404(RoomAsset, id=room_asset_id)
    
    if request.method == 'POST':
        form = RoomAssetForm(request.POST, instance=room_asset)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asset updated successfully!')
            return redirect('assets:room_assets_detail', room_id=room_asset.room.id)
    else:
        form = RoomAssetForm(instance=room_asset)
    
    context = {
        'form': form,
        'room_asset': room_asset,
    }
    return render(request, 'assets/edit_room_asset.html', context)

@login_required
def delete_room_asset(request, room_asset_id):
    """Delete room asset assignment"""
    room_asset = get_object_or_404(RoomAsset, id=room_asset_id)
    room_id = room_asset.room.id
    
    if request.method == 'POST':
        asset_name = room_asset.asset.name
        room_asset.delete()
        messages.success(request, f'{asset_name} removed from room successfully!')
        return redirect('assets:room_assets_detail', room_id=room_id)
    
    context = {
        'room_asset': room_asset,
    }
    return render(request, 'assets/delete_room_asset.html', context)

@login_required
def asset_maintenance(request, room_asset_id=None):
    """Log maintenance for an asset"""
    initial = {}
    if room_asset_id:
        room_asset = get_object_or_404(RoomAsset, id=room_asset_id)
        initial['room_asset'] = room_asset
    
    if request.method == 'POST':
        form = AssetMaintenanceForm(request.POST, initial=initial)
        if form.is_valid():
            maintenance = form.save()
            messages.success(request, 'Maintenance logged successfully!')
            
            # Update asset status if repaired
            if maintenance.maintenance_type == 'repair':
                maintenance.room_asset.status = 'working'
                maintenance.room_asset.save()
            
            return redirect('assets:maintenance_list')
    else:
        form = AssetMaintenanceForm(initial=initial)
    
    context = {
        'form': form,
    }
    return render(request, 'assets/asset_maintenance.html', context)

@login_required
def maintenance_list(request):
    """List all maintenance activities"""
    maintenance_logs = AssetMaintenanceLog.objects.select_related(
        'room_asset__room', 
        'room_asset__asset'
    ).order_by('-maintenance_date')
    
    context = {
        'maintenance_logs': maintenance_logs,
    }
    return render(request, 'assets/maintenance_list.html', context)

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
        # Handle audit item updates
        for item in audit_items:
            status_key = f"status_{item.id}"
            notes_key = f"notes_{item.id}"
            
            if status_key in request.POST:
                item.status = request.POST[status_key]
                item.condition_notes = request.POST.get(notes_key, '')
                item.save()
        
        # Mark audit as completed if requested
        if 'complete_audit' in request.POST:
            audit.completed = True
            audit.save()
            messages.success(request, 'Audit completed successfully!')
            return redirect('assets:monthly_audits')
    
    context = {
        'audit': audit,
        'audit_items': audit_items,
    }
    return render(request, 'assets/audit_detail.html', context)
@login_required
def create_monthly_audits(request):
    """Manually create monthly audits for all rooms"""
    current_month = datetime.now().strftime('%B %Y')
    
    if request.method == 'POST':
        today = timezone.now().date()
        first_day = today.replace(day=1)
        
        created_count = 0
        rooms = Room.objects.all()
        
        for room in rooms:
            # Check if audit already exists for this month
            existing_audit = MonthlyAudit.objects.filter(
                room=room,
                audit_date__year=first_day.year,
                audit_date__month=first_day.month
            ).exists()
            
            if not existing_audit:
                audit = MonthlyAudit.objects.create(
                    room=room,
                    audit_date=first_day,
                    auditor=request.user
                )
                
                # Create audit items for each room asset
                room_assets = RoomAsset.objects.filter(room=room)
                for room_asset in room_assets:
                    AuditItem.objects.create(
                        audit=audit,
                        room_asset=room_asset,
                        status=room_asset.status
                    )
                
                created_count += 1
        
        messages.success(request, f'Successfully created {created_count} monthly audits for {current_month}!')
        return redirect('assets:monthly_audits')
    
    context = {
        'current_month': current_month,
    }
    return render(request, 'assets/create_audits.html', context)

@login_required
def audit_detail(request, audit_id):
    """Detail view for a specific audit"""
    audit = get_object_or_404(MonthlyAudit, id=audit_id)
    audit_items = AuditItem.objects.filter(audit=audit).select_related('room_asset__asset')
    
    if request.method == 'POST':
        # Handle audit item updates
        for item in audit_items:
            status_key = f"status_{item.id}"
            notes_key = f"notes_{item.id}"
            
            if status_key in request.POST:
                item.status = request.POST[status_key]
                item.condition_notes = request.POST.get(notes_key, '')
                item.save()
        
        # Update audit notes
        audit_notes = request.POST.get('audit_notes', '')
        if audit_notes:
            audit.notes = audit_notes
            audit.save()
        
        # Mark audit as completed if requested
        if 'complete_audit' in request.POST:
            audit.completed = True
            audit.save()
            messages.success(request, 'Audit completed successfully!')
            return redirect('assets:monthly_audits')
        else:
            messages.success(request, 'Audit progress saved!')
            return redirect('assets:audit_detail', audit_id=audit.id)
    
    context = {
        'audit': audit,
        'audit_items': audit_items,
    }
    return render(request, 'assets/audit_detail.html', context)