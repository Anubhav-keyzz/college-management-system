# Course management views
# Admin can create/edit/delete courses and assign teachers and students

"""
courses/views.py — Views for course management (CRUD).

Access rules:
  - admin   : full create / edit / delete / view
  - teacher : view only their own assigned courses
  - student : view only their enrolled courses
"""

from django.shortcuts import render, redirect, get_object_or_404  # Rendering helpers
from django.contrib.auth.decorators import login_required         # Auth guard
from django.contrib import messages                               # Flash messages
from .models import Course                                        # Course model
from users.models import CustomUser                               # For teacher/student dropdowns


@login_required
def course_list(request):
    """
    Display the course list, filtered by the current user's role.

    Admin   → sees all courses with teacher info pre-fetched
    Teacher → sees only courses they teach
    Student → sees only courses they are enrolled in
    """
    u = request.user

    if u.is_admin:
        # select_related('teacher')     — avoids N+1 queries when accessing course.teacher
        # prefetch_related('students')  — efficiently loads the ManyToMany students
        courses = Course.objects.select_related('teacher').prefetch_related('students')
    elif u.is_teacher:
        # Filter to only courses where this user is the assigned teacher
        courses = Course.objects.filter(teacher=u)
    else:
        # Student: access via the reverse ManyToMany relation set during enrollment
        courses = u.enrolled_courses.select_related('teacher')

    return render(request, 'courses/course_list.html', {'courses': courses})


@login_required
def course_detail(request, pk):
    """
    Show the detail page for a single course identified by its primary key.
    Returns 404 if the course does not exist.
    """
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'courses/course_detail.html', {'course': course})


@login_required
def create_course(request):
    """
    Create a new course (admin only).

    GET  → Render empty form with teacher and student option lists.
    POST → Validate the course code for uniqueness, create the Course,
           assign teacher and enrolled students, then redirect.
    """
    # Non-admins cannot create courses
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('course_list')

    # Build option lists for the form dropdowns/multiselects
    teachers = CustomUser.objects.filter(role='teacher')
    students  = CustomUser.objects.filter(role='student')

    if request.method == 'POST':
        p = request.POST  # Shorthand for POST data

        # Prevent duplicate course codes before saving
        if Course.objects.filter(code=p['code']).exists():
            messages.error(request, 'Course code already exists.')
        else:
            # Build the Course instance from form data
            c = Course(
                name=p['name'],
                code=p['code'],
                description=p.get('description', ''),
                credits=p.get('credits', 3),
            )
            tid = p.get('teacher')
            if tid:
                # Assign the selected teacher (FK by ID)
                c.teacher_id = tid
            c.save()  # Must save before setting ManyToMany fields

            # Assign all selected student IDs to the course enrollment
            c.students.set(p.getlist('students'))

            messages.success(request, 'Course created!')
            return redirect('course_list')

    return render(request, 'courses/course_form.html', {
        'title': 'Create Course', 'action': 'Create',
        'teachers': teachers, 'students': students,
    })


@login_required
def edit_course(request, pk):
    """
    Edit an existing course (admin only).

    GET  → Render the form pre-filled with current course data.
    POST → Update all fields including teacher and student enrollment.
    """
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('course_list')

    # Fetch the course to edit, or 404
    course = get_object_or_404(Course, pk=pk)
    teachers = CustomUser.objects.filter(role='teacher')
    students  = CustomUser.objects.filter(role='student')

    if request.method == 'POST':
        p = request.POST

        # Update all editable fields on the existing object
        course.name        = p['name']
        course.code        = p['code']
        course.description = p.get('description', '')
        course.credits     = p.get('credits', 3)

        tid = p.get('teacher')
        # Set teacher to None if no teacher was selected (unassign)
        course.teacher_id = tid if tid else None

        course.save()  # Save scalar fields before updating ManyToMany

        # Replace the current student enrollment with the new selection
        course.students.set(p.getlist('students'))

        messages.success(request, 'Course updated!')
        return redirect('course_list')

    return render(request, 'courses/course_form.html', {
        'title': 'Edit Course', 'action': 'Update',
        'course': course, 'teachers': teachers, 'students': students,
    })


@login_required
def delete_course(request, pk):
    """
    Delete a course (admin only).

    GET  → Show delete confirmation page.
    POST → Permanently delete the course and redirect.
    """
    if not request.user.is_admin:
        return redirect('course_list')

    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted.')
        return redirect('course_list')

    # Show a confirmation page with a cancel link back to the list
    return render(request, 'courses/confirm_delete.html', {
        'obj': course, 'cancel_url': 'course_list',
    })
