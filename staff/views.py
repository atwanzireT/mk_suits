from django.shortcuts import render, redirect
from .models import Staff, StaffAttendance
from django.utils import timezone
from .forms import StaffForm, StaffAttendanceForm, StaffCheckoutForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

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
    attendance = StaffAttendance.objects.select_related('staff').all()
    return render(request, 'attendance_list.html', {'attendance': attendance})

# Mark Attendance
@login_required
def mark_attendance(request):
    form = StaffAttendanceForm(request.POST or None)
    today = timezone.now()  # Get today's date
    if form.is_valid():
        form.save()
        return redirect('attendance_list')
    return render(request, 'mark_attendance.html', {'form': form, 'today': today})


# Checkout Attendance
def checkout_attendance(request, pk):
    attendance_record = get_object_or_404(StaffAttendance, pk=pk)

    if attendance_record.time_out:
        return redirect('attendance_list')

    if request.method == 'POST':
        attendance_record.time_out = timezone.now().time()
        attendance_record.date_out = timezone.now().date()
        attendance_record.save()
        return redirect('attendance_list')
    
    current_time = timezone.now().time().strftime('%H:%M')
    current_date = timezone.now().date().strftime('%Y-%m-%d')

    return render(request, 'checkout_attendance.html', {
        'attendance': attendance_record,
        'current_time': current_time,
        'current_date': current_date,
    })
