# Classroom management views
# Admin creates classes, assigns teacher and students

"""
classes/views.py — Views for Classroom management (CRUD).

Access rules:
  - admin   : full create / edit / delete / view
  - teacher : view only classrooms they teach
  - student : view only classrooms they are enrolled in
"""

from django.shortcuts import render, redirect, get_object_or_404  # Rendering helpers
from django.contrib.auth.decorators import login_required         # Auth guard
from django.contrib import messages                               # Flash messages
from .models import Classroom                                     # Classroom model
from courses.models import Course                                 # For course dropdown
from users.models import CustomUser                               # For teacher/student dropdowns


@login_required
def class_list(request):
    """
    Display classrooms filtered by the current user's role.

    Admin   → all classrooms (with course and teacher data pre-fetched)
    Teacher → only classrooms they are assigned to teach
    Student → only classrooms they are enrolled in
    """
    u = request.user

    if u.is_admin:
        # Load all classrooms; select_related avoids extra DB hits for course/teacher
        classes = Classroom.objects.select_related('course', 'teacher')
    elif u.is_teacher:
        # Filter to classrooms where this teacher is assigned
        classes = Classroom.objects.filter(teacher=u).select_related('course')
    else:
        # Student: use the reverse relation from the ManyToMany enrollment
        classes = u.enrolled_classes.select_related('course', 'teacher')

    return render(request, 'classes/class_list.html', {'classes': classes})


@login_required
def class_detail(request, pk):
    """
    Show the detail page for a single classroom.
    Returns 404 if the classroom does not exist.
    """
    cls = get_object_or_404(Classroom, pk=pk)
    return render(request, 'classes/class_detail.html', {'cls': cls})


@login_required
def create_class(request):
    """
    Create a new classroom (admin only).

    GET  → Render empty form with course, teacher, and student option lists.
    POST → Build and save the Classroom; assign teacher and students; redirect.
    """
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('class_list')

    # Populate dropdown option lists for the template
    courses  = Course.objects.all()
    teachers = CustomUser.objects.filter(role='teacher')
    students = CustomUser.objects.filter(role='student')

    if request.method == 'POST':
        p = request.POST

        # Build the Classroom instance (don't save yet — need PK for ManyToMany)
        cls = Classroom(
            name=p['name'],
            section=p.get('section', ''),
            course_id=p['course'],          # FK — assign by ID directly
            schedule=p.get('schedule', ''),
            room_number=p.get('room_number', ''),
        )
        tid = p.get('teacher')
        if tid:
            cls.teacher_id = tid  # Assign teacher FK by ID

        cls.save()  # Must save before setting ManyToMany

        # Set enrolled students from the multi-select list
        cls.students.set(p.getlist('students'))

        messages.success(request, 'Class created!')
        return redirect('class_list')

    return render(request, 'classes/class_form.html', {
        'title': 'Create Class', 'action': 'Create',
        'courses': courses, 'teachers': teachers, 'students': students,
    })


@login_required
def edit_class(request, pk):
    """
    Edit an existing classroom (admin only).

    GET  → Render pre-filled form.
    POST → Update all fields and student/teacher assignments; redirect.
    """
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('class_list')

    cls      = get_object_or_404(Classroom, pk=pk)
    courses  = Course.objects.all()
    teachers = CustomUser.objects.filter(role='teacher')
    students = CustomUser.objects.filter(role='student')

    if request.method == 'POST':
        p = request.POST

        # Update all editable scalar fields
        cls.name        = p['name']
        cls.section     = p.get('section', '')
        cls.course_id   = p['course']
        cls.schedule    = p.get('schedule', '')
        cls.room_number = p.get('room_number', '')

        tid = p.get('teacher')
        # Allow unassigning the teacher by setting to None
        cls.teacher_id = tid if tid else None

        cls.save()  # Save scalar fields first

        # Replace current student enrollment with the new selection
        cls.students.set(p.getlist('students'))

        messages.success(request, 'Class updated!')
        return redirect('class_list')

    return render(request, 'classes/class_form.html', {
        'title': 'Edit Class', 'action': 'Update', 'cls': cls,
        'courses': courses, 'teachers': teachers, 'students': students,
    })


@login_required
def delete_class(request, pk):
    """
    Delete a classroom (admin only).

    GET  → Show delete confirmation page.
    POST → Delete the classroom and redirect to the list.
    """
    if not request.user.is_admin:
        return redirect('class_list')

    cls = get_object_or_404(Classroom, pk=pk)

    if request.method == 'POST':
        cls.delete()
        messages.success(request, 'Class deleted.')
        return redirect('class_list')

    return render(request, 'classes/confirm_delete.html', {
        'obj': cls, 'cancel_url': 'class_list',
    })
