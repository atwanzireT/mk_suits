from django.shortcuts import render, redirect
from .models import Staff, StaffAttendance
from django.utils import timezone
from .forms import StaffForm, StaffAttendanceForm, StaffCheckoutForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator

# Staff List
@login_required
def staff_list(request):
    staff = Staff.objects.all()
    return render(request, 'staff_list.html', {'staff': staff})

# Add Staff
@login_required
def add_staff(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('staff_list')
    return render(request, 'add_staff.html', {'form': form})

# Attendance List


@login_required
def attendance_list(request):
    today = now().date()

    # Get up to 10 records from today
    todays_attendance = StaffAttendance.objects.select_related('staff') \
        .filter(date=today) \
        .order_by('-time_in')[:10]

    # Get remaining records (older than today OR overflow from today)
    excluded_ids = todays_attendance.values_list('id', flat=True)
    other_attendance = StaffAttendance.objects.select_related('staff') \
        .exclude(id__in=excluded_ids) \
        .order_by('-date', '-time_in')

    # Paginate other records (starting from page 2)
    paginator = Paginator(other_attendance, 10)
    page_number = request.GET.get('page', '1')

    if page_number == '1':
        # Combine today's attendance with remaining (if < 10, fill from others)
        remaining_slots = 10 - len(todays_attendance)
        if remaining_slots > 0:
            extra_records = other_attendance[:remaining_slots]
            records_to_display = list(todays_attendance) + list(extra_records)
        else:
            records_to_display = todays_attendance
        is_first_page = True
    else:
        # Use paginator for other pages
        page_obj = paginator.get_page(page_number)
        records_to_display = page_obj
        is_first_page = False

    context = {
        'records': records_to_display,
        'is_first_page': is_first_page,
    }

    if not is_first_page:
        context['page_obj'] = page_obj

    return render(request, 'attendance_list.html', context)

# Mark Attendance
@login_required
def mark_attendance(request):
    form = StaffAttendanceForm(request.POST or None )
    today = timezone.now()  # Get today's date
    if form.is_valid():
        form.save()
        return redirect('attendance_list')
    return render(request, 'mark_attendance.html', {'form': form, 'today': today})

from django.utils.timezone import now
from datetime import datetime

def checkout_attendance(request, pk):
    attendance_record = get_object_or_404(StaffAttendance, pk=pk)

    if attendance_record.time_out:
        return redirect('attendance_list')

    if request.method == 'POST':
        # Get user-submitted time and date
        time_out_str = request.POST.get('time_out')
        date_out_str = request.POST.get('date_out')

        try:
            # Parse time_out (format: 'HH:MM')
            time_out = datetime.strptime(time_out_str, '%H:%M').time()
            attendance_record.time_out = time_out
        except (ValueError, TypeError):
            # Fallback to current time if invalid
            attendance_record.time_out = now().time()

        try:
            # Parse date_out (format: 'YYYY-MM-DD')
            date_out = datetime.strptime(date_out_str, '%Y-%m-%d').date()
            attendance_record.date_out = date_out
        except (ValueError, TypeError):
            # Fallback to current date if invalid
            attendance_record.date_out = now().date()

        attendance_record.save()
        return redirect('attendance_list')

    # Default values for the form (pre-filled with current time/date)
    default_time_out = now().strftime('%H:%M')  # Format: '14:30'
    default_date_out = attendance_record.date.strftime('%Y-%m-%d')  # Use check-in date as default

    return render(request, 'checkout_attendance.html', {
        'attendance': attendance_record,
        'default_time_out': default_time_out,
        'default_date_out': default_date_out,
    })
    
@login_required
def staff_detail(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    return render(request, 'staff_detail.html', {'staff': staff})


@login_required
def edit_staff(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    form = StaffForm(request.POST or None,
                     request.FILES or None, instance=staff)
    if form.is_valid():
        form.save()
        return redirect('staff_list')
    return render(request, 'edit_staff.html', {'form': form, 'staff': staff})
