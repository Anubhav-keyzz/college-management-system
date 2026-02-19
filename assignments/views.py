# Assignment views
# Full lifecycle: create, submit, grade, view feedback

"""
assignments/views.py — Views for assignment management, submission, and grading.

Handles:
  - assignment_list   : list assignments (role-filtered)
  - assignment_detail : view one assignment; students see their submission,
                        teachers/admins see all submissions
  - create_assignment : teachers and admins post new assignments
  - edit_assignment   : update an existing assignment
  - delete_assignment : remove an assignment
  - submit_assignment : student uploads their answer (file and/or text)
                        with a 500 KB file-size guard
  - grade_submission  : teacher awards marks and writes feedback
"""

from django.shortcuts import render, redirect, get_object_or_404  # Rendering helpers
from django.contrib.auth.decorators import login_required         # Auth guard
from django.contrib import messages                               # Flash messages
from .models import Assignment, AssignmentSubmission              # Our models
from classes.models import Classroom                              # For classroom dropdown


# ─────────────────────────────────────────────────────────────────────────────
# File-size limit for student submissions (500 KB)
# Used in submit_assignment to reject oversized uploads before saving.
MAX_SUBMISSION_SIZE = 500 * 1024  # 500 KB in bytes
# ─────────────────────────────────────────────────────────────────────────────


@login_required
def assignment_list(request):
    """
    Display assignments filtered by the current user's role.

    Admin   → all assignments (with classroom and uploader info)
    Teacher → only assignments they uploaded
    Student → only assignments for classrooms they are enrolled in
    """
    u = request.user

    if u.is_admin:
        # select_related fetches classroom and uploaded_by in a single JOIN query
        assignments = Assignment.objects.select_related('classroom', 'uploaded_by')
    elif u.is_teacher:
        # Filter to assignments this teacher created
        assignments = Assignment.objects.filter(
            uploaded_by=u
        ).select_related('classroom')
    else:
        # Student: assignments for all classrooms they're enrolled in
        assignments = Assignment.objects.filter(
            classroom__in=u.enrolled_classes.all()
        ).select_related('classroom', 'uploaded_by')

    return render(request, 'assignments/assignment_list.html', {
        'assignments': assignments
    })


@login_required
def assignment_detail(request, pk):
    """
    Show detail for a single assignment.

    - Students  : see their own submission (or a prompt to submit)
    - Teachers/Admins : see a table of all student submissions
    """
    a = get_object_or_404(Assignment, pk=pk)
    u = request.user

    submission  = None   # For students: their own submission
    submissions = None   # For teachers/admins: all submissions

    if u.is_student:
        # Try to find this student's submission for the assignment (may be None)
        submission = AssignmentSubmission.objects.filter(
            assignment=a, student=u
        ).first()
    elif u.is_teacher or u.is_admin:
        # Load all submissions with student info pre-fetched
        submissions = a.submissions.select_related('student').all()

    return render(request, 'assignments/assignment_detail.html', {
        'assignment':  a,
        'submission':  submission,
        'submissions': submissions,
    })


@login_required
def create_assignment(request):
    """
    Create a new assignment (teachers and admins only).

    Teachers only see their own classrooms in the dropdown.
    Admins see all classrooms.

    GET  → Render empty assignment form.
    POST → Build and save the Assignment; optionally attach a file.
    """
    if not (request.user.is_teacher or request.user.is_admin):
        messages.error(request, 'Access denied.')
        return redirect('assignment_list')

    u = request.user

    # Build the classroom dropdown based on role
    if u.is_teacher:
        classes = Classroom.objects.filter(teacher=u)  # Only their own classrooms
    else:
        classes = Classroom.objects.all()              # Admins see everything

    if request.method == 'POST':
        p = request.POST

        # Build the Assignment object from form data
        a = Assignment(
            title=p['title'],
            description=p.get('description', ''),
            classroom_id=p['classroom'],      # FK assigned by ID
            uploaded_by=u,                   # Automatically set to current user
            max_marks=p.get('max_marks', 100),
        )

        # Only set due_date if provided (it's optional)
        if p.get('due_date'):
            a.due_date = p['due_date']

        # Attach uploaded file if one was provided
        if request.FILES.get('file'):
            a.file = request.FILES['file']

        a.save()
        messages.success(request, 'Assignment created!')
        return redirect('assignment_list')

    return render(request, 'assignments/assignment_form.html', {
        'title': 'Create Assignment', 'action': 'Create', 'classes': classes,
    })


@login_required
def edit_assignment(request, pk):
    """
    Edit an existing assignment.

    Access: admins can edit any assignment; teachers can only edit their own.

    GET  → Render the pre-filled assignment form.
    POST → Update all fields; replace the file if a new one is uploaded.
    """
    a = get_object_or_404(Assignment, pk=pk)

    # Only the creator or an admin may edit
    if not (request.user.is_admin or a.uploaded_by == request.user):
        messages.error(request, 'Access denied.')
        return redirect('assignment_list')

    u = request.user
    classes = (
        Classroom.objects.filter(teacher=u) if u.is_teacher
        else Classroom.objects.all()
    )

    if request.method == 'POST':
        p = request.POST

        # Update all editable fields on the existing assignment object
        a.title        = p['title']
        a.description  = p.get('description', '')
        a.classroom_id = p['classroom']
        a.max_marks    = p.get('max_marks', 100)

        if p.get('due_date'):
            a.due_date = p['due_date']

        # Replace file only if a new file was uploaded
        if request.FILES.get('file'):
            a.file = request.FILES['file']

        a.save()
        messages.success(request, 'Assignment updated!')
        return redirect('assignment_list')

    return render(request, 'assignments/assignment_form.html', {
        'title': 'Edit Assignment', 'action': 'Update',
        'assignment': a, 'classes': classes,
    })


@login_required
def delete_assignment(request, pk):
    """
    Delete an assignment.

    Access: admins can delete any; teachers can only delete their own.

    GET  → Show confirmation page.
    POST → Delete and redirect to list.
    """
    a = get_object_or_404(Assignment, pk=pk)

    if not (request.user.is_admin or a.uploaded_by == request.user):
        return redirect('assignment_list')

    if request.method == 'POST':
        a.delete()
        messages.success(request, 'Assignment deleted.')
        return redirect('assignment_list')

    return render(request, 'assignments/confirm_delete.html', {
        'obj': a, 'cancel_url': 'assignment_list',
    })


@login_required
def submit_assignment(request, pk):
    """
    Allow a student to submit their work for an assignment.

    - Only students can submit.
    - Enforces a 500 KB file-size limit on uploaded files.
    - Uses get_or_create so re-submitting overwrites the previous submission
      rather than creating a duplicate (unique_together enforces one-per-student).

    GET  → Show the submission form (pre-filled if already submitted).
    POST → Validate file size, save submission text and/or file, redirect.
    """
    a = get_object_or_404(Assignment, pk=pk)

    # Only students may submit
    if not request.user.is_student:
        return redirect('assignment_list')

    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')

        # ── File size guard ────────────────────────────────────────────────────
        # Reject files larger than 500 KB before saving to disk
        if uploaded_file and uploaded_file.size > MAX_SUBMISSION_SIZE:
            messages.error(
                request,
                f'File too large. Max allowed is 500 KB. '
                f'Your file is {uploaded_file.size // 1024} KB.'
            )
            # Re-show the form with the existing submission info
            submission = AssignmentSubmission.objects.filter(
                assignment=a, student=request.user
            ).first()
            return render(request, 'assignments/submit_assignment.html', {
                'assignment': a, 'submission': submission,
            })
        # ──────────────────────────────────────────────────────────────────────

        # get_or_create returns (instance, created_bool)
        # If the student already submitted, we update it; otherwise create new.
        sub, _ = AssignmentSubmission.objects.get_or_create(
            assignment=a, student=request.user
        )
        sub.text = request.POST.get('text', '')  # Save text answer (may be empty)

        if uploaded_file:
            sub.file = uploaded_file  # Save the uploaded file

        sub.save()
        messages.success(request, 'Assignment submitted!')
        return redirect('assignment_detail', pk=pk)

    # GET: load existing submission (if any) to pre-fill the form
    submission = AssignmentSubmission.objects.filter(
        assignment=a, student=request.user
    ).first()

    return render(request, 'assignments/submit_assignment.html', {
        'assignment': a, 'submission': submission,
    })


@login_required
def grade_submission(request, sub_id):
    """
    Allow a teacher or admin to grade a student's submission.

    GET  → Show grading form with the submission details.
    POST → Save marks, feedback, and mark as graded; redirect to assignment detail.
    """
    sub = get_object_or_404(AssignmentSubmission, pk=sub_id)

    # Only teachers and admins may grade
    if not (request.user.is_teacher or request.user.is_admin):
        return redirect('assignment_list')

    if request.method == 'POST':
        sub.marks     = request.POST.get('marks')         # Awarded marks (integer)
        sub.feedback  = request.POST.get('feedback', '')  # Optional written feedback
        sub.is_graded = True                              # Mark as graded
        sub.save()

        messages.success(request, 'Submission graded!')
        # Redirect back to the parent assignment's detail page
        return redirect('assignment_detail', pk=sub.assignment.pk)

    return render(request, 'assignments/grade_submission.html', {'sub': sub})
