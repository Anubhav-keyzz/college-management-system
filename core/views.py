import io
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from users.models import CustomUser
from courses.models import Course
from classes.models import Classroom
from attendance.models import AttendanceSession, AttendanceRecord
from assignments.models import Assignment, AssignmentSubmission


@login_required
def dashboard(request):
    u = request.user
    ctx = {}
    if u.is_admin:
        ctx['total_students'] = CustomUser.objects.filter(role='student').count()
        ctx['total_teachers'] = CustomUser.objects.filter(role='teacher').count()
        ctx['total_courses'] = Course.objects.count()
        ctx['total_classes'] = Classroom.objects.count()
        ctx['recent_sessions'] = AttendanceSession.objects.select_related('classroom', 'taken_by').order_by('-date')[:5]
        ctx['recent_assignments'] = Assignment.objects.select_related('classroom', 'uploaded_by').order_by('-created_at')[:5]
    elif u.is_teacher:
        my_classes = Classroom.objects.filter(teacher=u)
        ctx['my_classes'] = my_classes
        ctx['total_students'] = sum(c.students.count() for c in my_classes)
        ctx['my_courses'] = Course.objects.filter(teacher=u).count()
        ctx['recent_assignments'] = Assignment.objects.filter(uploaded_by=u).order_by('-created_at')[:5]
        ctx['recent_sessions'] = AttendanceSession.objects.filter(taken_by=u).order_by('-date')[:5]
    else:
        ctx['my_courses'] = u.enrolled_courses.all()
        ctx['my_classes'] = u.enrolled_classes.select_related('teacher', 'course').all()
        ctx['recent_assignments'] = Assignment.objects.filter(
            classroom__in=u.enrolled_classes.all()
        ).order_by('-created_at')[:5]
        ctx['attendance_pct'] = _student_attendance_pct(u)
    return render(request, 'core/dashboard.html', ctx)


def _student_attendance_pct(student):
    total = AttendanceRecord.objects.filter(student=student).count()
    present = AttendanceRecord.objects.filter(student=student, status__in=['present', 'late']).count()
    return round(present / total * 100, 1) if total > 0 else 0


# ─────────────────────────────────────────────────────────────
#  EXCEL EXPORT
# ─────────────────────────────────────────────────────────────

@login_required
def export_excel(request):
    """Export CMS data to a styled Excel (.xlsx) file."""
    if not request.user.is_admin:
        return redirect('dashboard')

    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill
    except ImportError:
        return HttpResponse(
            "openpyxl is not installed. Run: python -m pip install openpyxl",
            status=500
        )

    wb = openpyxl.Workbook()
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(fill_type="solid", fgColor="4F46E5")

    def style_headers(ws):
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill

    # ── Sheet 1: Summary ──────────────────────────────────────
    ws1 = wb.active
    ws1.title = "Summary"
    ws1.append(["Metric", "Count"])
    style_headers(ws1)
    ws1.append(["Total Students",    CustomUser.objects.filter(role='student').count()])
    ws1.append(["Total Teachers",    CustomUser.objects.filter(role='teacher').count()])
    ws1.append(["Total Admins",      CustomUser.objects.filter(role='admin').count()])
    ws1.append(["Total Courses",     Course.objects.count()])
    ws1.append(["Total Classes",     Classroom.objects.count()])
    ws1.append(["Total Assignments", Assignment.objects.count()])
    ws1.append(["Total Submissions", AssignmentSubmission.objects.count()])
    ws1.column_dimensions["A"].width = 25
    ws1.column_dimensions["B"].width = 15

    # ── Sheet 2: Students ─────────────────────────────────────
    ws2 = wb.create_sheet("Students")
    ws2.append(["#", "Full Name", "Username", "Email", "Phone", "Date of Birth"])
    style_headers(ws2)
    for idx, s in enumerate(CustomUser.objects.filter(role='student').order_by('last_name'), 1):
        ws2.append([
            idx,
            s.get_full_name() or s.username,
            s.username,
            s.email or "",
            str(s.phone or ""),
            str(s.date_of_birth or ""),
        ])
    for col in ["A", "B", "C", "D", "E", "F"]:
        ws2.column_dimensions[col].width = 20

    # ── Sheet 3: Teachers ─────────────────────────────────────
    ws3 = wb.create_sheet("Teachers")
    ws3.append(["#", "Full Name", "Username", "Email", "Phone"])
    style_headers(ws3)
    for idx, t in enumerate(CustomUser.objects.filter(role='teacher').order_by('last_name'), 1):
        ws3.append([
            idx,
            t.get_full_name() or t.username,
            t.username,
            t.email or "",
            str(t.phone or ""),
        ])
    for col in ["A", "B", "C", "D", "E"]:
        ws3.column_dimensions[col].width = 22

    # ── Sheet 4: Courses ──────────────────────────────────────
    ws4 = wb.create_sheet("Courses")
    ws4.append(["#", "Course Name", "Course Code"])
    style_headers(ws4)
    for idx, c in enumerate(Course.objects.all(), 1):
        code = getattr(c, 'code', getattr(c, 'course_code', ''))
        ws4.append([idx, c.name, str(code)])
    for col in ["A", "B", "C"]:
        ws4.column_dimensions[col].width = 25

    # ── Sheet 5: Assignments ──────────────────────────────────
    ws5 = wb.create_sheet("Assignments")
    ws5.append(["#", "Title", "Classroom", "Uploaded By", "Due Date", "Max Marks", "Submissions"])
    style_headers(ws5)
    for idx, a in enumerate(
        Assignment.objects.select_related('classroom', 'uploaded_by').all(), 1
    ):
        ws5.append([
            idx,
            a.title,
            str(a.classroom),
            a.uploaded_by.get_full_name() or a.uploaded_by.username,
            str(a.due_date or "No deadline"),
            a.max_marks,
            a.submissions.count(),
        ])
    for col in ["A", "B", "C", "D", "E", "F", "G"]:
        ws5.column_dimensions[col].width = 22

    # ── Stream response ───────────────────────────────────────
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="cms_report.xlsx"'
    return response


# ─────────────────────────────────────────────────────────────
#  PDF EXPORT
# ─────────────────────────────────────────────────────────────

@login_required
def export_pdf(request):
    """Export CMS data to a formatted PDF file."""
    if not request.user.is_admin:
        return redirect('dashboard')

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except ImportError:
        return HttpResponse(
            "reportlab is not installed. Run: python -m pip install reportlab",
            status=500
        )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    styles = getSampleStyleSheet()
    primary = colors.HexColor('#4F46E5')
    elements = []

    title_style = ParagraphStyle(
        'CMSTitle', parent=styles['Title'],
        textColor=primary, fontSize=20, spaceAfter=6,
    )
    heading_style = ParagraphStyle(
        'CMSHeading', parent=styles['Heading2'],
        textColor=primary, spaceBefore=16, spaceAfter=6,
    )

    elements.append(Paragraph("College Management System — Report", title_style))
    elements.append(Paragraph(
        "Generated by: " + (request.user.get_full_name() or request.user.username),
        styles['Normal'],
    ))
    elements.append(Spacer(1, 0.4*cm))

    def make_table(data, col_widths=None):
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0),  primary),
            ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.white),
            ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, 0),  10),
            ('TOPPADDING',    (0, 0), (-1, 0),  8),
            ('BOTTOMPADDING', (0, 0), (-1, 0),  8),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.white, colors.HexColor('#F1F5F9')]),
            ('FONTSIZE',      (0, 1), (-1, -1), 9),
            ('TOPPADDING',    (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        return t

    # Summary
    elements.append(Paragraph("Summary", heading_style))
    elements.append(make_table([
        ["Metric", "Count"],
        ["Total Students",    CustomUser.objects.filter(role='student').count()],
        ["Total Teachers",    CustomUser.objects.filter(role='teacher').count()],
        ["Total Admins",      CustomUser.objects.filter(role='admin').count()],
        ["Total Courses",     Course.objects.count()],
        ["Total Classes",     Classroom.objects.count()],
        ["Total Assignments", Assignment.objects.count()],
        ["Total Submissions", AssignmentSubmission.objects.count()],
    ], col_widths=[10*cm, 5*cm]))

    # Students
    elements.append(Spacer(1, 0.4*cm))
    elements.append(Paragraph("Students", heading_style))
    rows = [["#", "Full Name", "Username", "Email"]]
    for idx, s in enumerate(CustomUser.objects.filter(role='student').order_by('last_name'), 1):
        rows.append([str(idx), s.get_full_name() or s.username, s.username, s.email or "—"])
    elements.append(
        make_table(rows, col_widths=[1*cm, 5*cm, 4*cm, 6*cm])
        if len(rows) > 1 else Paragraph("No students found.", styles['Normal'])
    )

    # Teachers
    elements.append(Spacer(1, 0.4*cm))
    elements.append(Paragraph("Teachers", heading_style))
    rows = [["#", "Full Name", "Username", "Email"]]
    for idx, t in enumerate(CustomUser.objects.filter(role='teacher').order_by('last_name'), 1):
        rows.append([str(idx), t.get_full_name() or t.username, t.username, t.email or "—"])
    elements.append(
        make_table(rows, col_widths=[1*cm, 5*cm, 4*cm, 6*cm])
        if len(rows) > 1 else Paragraph("No teachers found.", styles['Normal'])
    )

    # Courses
    elements.append(Spacer(1, 0.4*cm))
    elements.append(Paragraph("Courses", heading_style))
    rows = [["#", "Course Name", "Code"]]
    for idx, c in enumerate(Course.objects.all(), 1):
        code = getattr(c, 'code', getattr(c, 'course_code', ''))
        rows.append([str(idx), c.name, str(code)])
    elements.append(
        make_table(rows, col_widths=[1*cm, 9*cm, 6*cm])
        if len(rows) > 1 else Paragraph("No courses found.", styles['Normal'])
    )

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="cms_report.pdf"'
    return response