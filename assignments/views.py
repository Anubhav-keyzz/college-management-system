from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Assignment, AssignmentSubmission
from classes.models import Classroom


@login_required
def assignment_list(request):
    u = request.user
    if u.is_admin:
        assignments = Assignment.objects.select_related('classroom', 'uploaded_by')
    elif u.is_teacher:
        assignments = Assignment.objects.filter(uploaded_by=u).select_related('classroom')
    else:
        assignments = Assignment.objects.filter(classroom__in=u.enrolled_classes.all()).select_related('classroom', 'uploaded_by')
    return render(request, 'assignments/assignment_list.html', {'assignments': assignments})


@login_required
def assignment_detail(request, pk):
    a = get_object_or_404(Assignment, pk=pk)
    u = request.user
    submission = None
    submissions = None
    if u.is_student:
        submission = AssignmentSubmission.objects.filter(assignment=a, student=u).first()
    elif u.is_teacher or u.is_admin:
        submissions = a.submissions.select_related('student').all()
    return render(request, 'assignments/assignment_detail.html', {
        'assignment': a, 'submission': submission, 'submissions': submissions
    })


@login_required
def create_assignment(request):
    if not (request.user.is_teacher or request.user.is_admin):
        messages.error(request, 'Access denied.')
        return redirect('assignment_list')
    u = request.user
    if u.is_teacher:
        classes = Classroom.objects.filter(teacher=u)
    else:
        classes = Classroom.objects.all()
    if request.method == 'POST':
        p = request.POST
        a = Assignment(
            title=p['title'], description=p.get('description',''),
            classroom_id=p['classroom'], uploaded_by=u,
            max_marks=p.get('max_marks', 100),
        )
        if p.get('due_date'):
            a.due_date = p['due_date']
        if request.FILES.get('file'):
            a.file = request.FILES['file']
        a.save()
        messages.success(request, 'Assignment created!')
        return redirect('assignment_list')
    return render(request, 'assignments/assignment_form.html', {
        'title': 'Create Assignment', 'action': 'Create', 'classes': classes
    })

MAX_SUBMISSION_SIZE = 500 * 1024  # 500 KB

@login_required
def submit_assignment(request, pk):
    a = get_object_or_404(Assignment, pk=pk)
    if not request.user.is_student:
        return redirect('assignment_list')
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        # ── 500 KB guard ──────────────────────────────────────
        if uploaded_file and uploaded_file.size > MAX_SUBMISSION_SIZE:
            messages.error(request, f'File too large. Max allowed is 500 KB. Your file is {uploaded_file.size // 1024} KB.')
            submission = AssignmentSubmission.objects.filter(assignment=a, student=request.user).first()
            return render(request, 'assignments/submit_assignment.html', {'assignment': a, 'submission': submission})
        # ─────────────────────────────────────────────────────
        sub, _ = AssignmentSubmission.objects.get_or_create(assignment=a, student=request.user)
        sub.text = request.POST.get('text', '')
        if uploaded_file:
            sub.file = uploaded_file
        sub.save()
        ...


@login_required
def edit_assignment(request, pk):
    a = get_object_or_404(Assignment, pk=pk)
    if not (request.user.is_admin or a.uploaded_by == request.user):
        messages.error(request, 'Access denied.')
        return redirect('assignment_list')
    u = request.user
    classes = Classroom.objects.filter(teacher=u) if u.is_teacher else Classroom.objects.all()
    if request.method == 'POST':
        p = request.POST
        a.title = p['title']
        a.description = p.get('description', '')
        a.classroom_id = p['classroom']
        a.max_marks = p.get('max_marks', 100)
        if p.get('due_date'):
            a.due_date = p['due_date']
        if request.FILES.get('file'):
            a.file = request.FILES['file']
        a.save()
        messages.success(request, 'Assignment updated!')
        return redirect('assignment_list')
    return render(request, 'assignments/assignment_form.html', {
        'title': 'Edit Assignment', 'action': 'Update', 'assignment': a, 'classes': classes
    })


@login_required
def delete_assignment(request, pk):
    a = get_object_or_404(Assignment, pk=pk)
    if not (request.user.is_admin or a.uploaded_by == request.user):
        return redirect('assignment_list')
    if request.method == 'POST':
        a.delete()
        messages.success(request, 'Assignment deleted.')
        return redirect('assignment_list')
    return render(request, 'assignments/confirm_delete.html', {'obj': a, 'cancel_url': 'assignment_list'})


@login_required
def submit_assignment(request, pk):
    a = get_object_or_404(Assignment, pk=pk)
    if not request.user.is_student:
        return redirect('assignment_list')
    if request.method == 'POST':
        sub, _ = AssignmentSubmission.objects.get_or_create(assignment=a, student=request.user)
        sub.text = request.POST.get('text', '')
        if request.FILES.get('file'):
            sub.file = request.FILES['file']
        sub.save()
        messages.success(request, 'Assignment submitted!')
        return redirect('assignment_detail', pk=pk)
    submission = AssignmentSubmission.objects.filter(assignment=a, student=request.user).first()
    return render(request, 'assignments/submit_assignment.html', {'assignment': a, 'submission': submission})


@login_required
def grade_submission(request, sub_id):
    sub = get_object_or_404(AssignmentSubmission, pk=sub_id)
    if not (request.user.is_teacher or request.user.is_admin):
        return redirect('assignment_list')
    if request.method == 'POST':
        sub.marks = request.POST.get('marks')
        sub.feedback = request.POST.get('feedback', '')
        sub.is_graded = True
        sub.save()
        messages.success(request, 'Submission graded!')
        return redirect('assignment_detail', pk=sub.assignment.pk)
    return render(request, 'assignments/grade_submission.html', {'sub': sub})
