# Attendance views
# Teachers take attendance, view reports and session history

"""
attendance/views.py — Views for recording and reporting student attendance.

Handles:
  - attendance_list   : list all sessions (role-filtered)
  - take_attendance   : record attendance for a classroom on a given date
  - attendance_report : aggregate attendance stats per student for a classroom
  - session_detail    : view individual records for one session
"""

from django.shortcuts import render, redirect, get_object_or_404  # Rendering helpers
from django.contrib.auth.decorators import login_required         # Auth guard
from django.contrib import messages                               # Flash messages
from django.utils import timezone                                 # Timezone-aware datetime
from .models import AttendanceSession, AttendanceRecord           # Our attendance models
from classes.models import Classroom                              # To look up classrooms
from users.models import CustomUser                               # For student lookups


@login_required
def attendance_list(request):
    """
    Display attendance sessions filtered by the current user's role.

    Admin   → all sessions with classroom and teacher info
    Teacher → only sessions they recorded
    Student → only sessions belonging to classrooms they are enrolled in
    """
    u = request.user

    if u.is_admin:
        # Load every session; select_related avoids extra queries for classroom/teacher
        sessions = AttendanceSession.objects.select_related(
            'classroom', 'taken_by'
        ).order_by('-date')
    elif u.is_teacher:
        # Only sessions this teacher created
        sessions = AttendanceSession.objects.filter(
            taken_by=u
        ).select_related('classroom').order_by('-date')
    else:
        # Student: sessions for classrooms they are enrolled in
        sessions = AttendanceSession.objects.filter(
            classroom__in=u.enrolled_classes.all()
        ).order_by('-date')

    return render(request, 'attendance/attendance_list.html', {'sessions': sessions})


@login_required
def take_attendance(request, class_id):
    """
    Record or update attendance for a specific classroom on a chosen date.

    Access: teachers and admins only. Teachers can only take attendance for
    classrooms assigned to them.

    GET  → Show the attendance form for the selected date (defaults to today).
           Pre-fills any already-saved status/notes.
    POST → Save (insert or update) one AttendanceRecord per student.

    URL query param:
      ?date=YYYY-MM-DD  — defaults to today if omitted or invalid
    """
    # Restrict access to staff roles
    if not (request.user.is_teacher or request.user.is_admin):
        messages.error(request, 'Access denied.')
        return redirect('attendance_list')

    # Fetch the classroom or return 404
    classroom = get_object_or_404(Classroom, pk=class_id)

    # Teachers may only record attendance for their own classrooms
    if request.user.is_teacher and classroom.teacher != request.user:
        messages.error(request, 'You are not assigned to this class.')
        return redirect('attendance_list')

    # Determine which date to record attendance for
    today    = timezone.now().date()
    date_str = request.GET.get('date', str(today))  # Default to today

    try:
        from datetime import date
        selected_date = date.fromisoformat(date_str)  # Parse YYYY-MM-DD string
    except (ValueError, TypeError):
        # Fall back to today if the date string is invalid
        selected_date = today

    # Get or create an AttendanceSession for this classroom on the selected date.
    # 'defaults' are only applied when creating a new session (not on get).
    session, created = AttendanceSession.objects.get_or_create(
        classroom=classroom,
        date=selected_date,
        defaults={'taken_by': request.user},
    )

    # All students enrolled in this classroom
    students = classroom.students.all()

    if request.method == 'POST':
        # Process each student's submitted status and note
        for student in students:
            status = request.POST.get(f'status_{student.pk}', 'absent')
            note   = request.POST.get(f'note_{student.pk}', '')

            # update_or_create: update existing record or insert a new one
            AttendanceRecord.objects.update_or_create(
                session=session,
                student=student,
                defaults={'status': status, 'note': note},
            )

        messages.success(request, 'Attendance saved!')
        return redirect('attendance_list')

    # ── Build per-student data for the form (GET) ──────────────────────────
    # Load existing records keyed by student ID for fast lookup
    existing = {r.student_id: r for r in session.records.all()}

    student_data = []
    for s in students:
        rec = existing.get(s.pk)  # None if no record saved yet
        student_data.append({
            'student': s,
            # Pre-fill status from existing record, or default to 'present'
            'status': rec.status if rec else 'present',
            'note':   rec.note   if rec else '',
        })

    return render(request, 'attendance/take_attendance.html', {
        'classroom':    classroom,
        'date':         selected_date,
        'student_data': student_data,
        'session':      session,
    })


@login_required
def attendance_report(request, class_id):
    """
    Generate an attendance summary report for a classroom.

    For each enrolled student, calculates:
      - total sessions
      - present / late / absent counts
      - attendance percentage (present + late counts as attended)
    """
    classroom = get_object_or_404(Classroom, pk=class_id)

    # All sessions for this classroom ordered chronologically
    sessions = AttendanceSession.objects.filter(
        classroom=classroom
    ).prefetch_related('records__student').order_by('date')

    students = classroom.students.all()
    report   = []

    for student in students:
        total   = sessions.count()  # Total number of sessions held

        # Count records where this student was marked present in this classroom
        present = AttendanceRecord.objects.filter(
            session__classroom=classroom, student=student, status='present'
        ).count()

        # Count records where this student was marked late
        late = AttendanceRecord.objects.filter(
            session__classroom=classroom, student=student, status='late'
        ).count()

        # Absent = total sessions minus present and late
        absent = total - present - late

        # Attendance percentage: present + late both count as "attended"
        pct = round((present + late) / total * 100, 1) if total > 0 else 0

        report.append({
            'student': student,
            'present': present,
            'late':    late,
            'absent':  absent,
            'total':   total,
            'pct':     pct,
        })

    return render(request, 'attendance/attendance_report.html', {
        'classroom': classroom,
        'report':    report,
        'sessions':  sessions,
    })


@login_required
def session_detail(request, session_id):
    """
    Show all attendance records for a single session.

    Uses select_related('student') to fetch student info in one query
    instead of N separate queries for N records.
    """
    session = get_object_or_404(AttendanceSession, pk=session_id)
    records = session.records.select_related('student').all()

    return render(request, 'attendance/session_detail.html', {
        'session': session,
        'records': records,
    })
