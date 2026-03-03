import os

# ── Python file comments ──────────────────────────────────────────
python_comments = {
    'manage.py': '# Entry point for Django management commands\n# Run: python manage.py runserver\n',
    'requirements.txt': '# Project dependencies\n# Install with: pip install -r requirements.txt\n',

    'college_management/settings.py': '# Django project settings and configuration\n# Database, installed apps, middleware, templates\n',
    'college_management/urls.py': '# Main URL configuration\n# Routes requests to appropriate app URLs\n',
    'college_management/wsgi.py': '# WSGI configuration for deployment\n',

    'core/views.py': '# Core views - handles dashboard logic\n# Shows different stats based on user role (admin/teacher/student)\n',
    'core/urls.py': '# Core URL patterns - login, logout, dashboard\n',
    'core/models.py': '# Core app models - no models needed here\n',
    'core/admin.py': '# Core admin registration\n',

    'users/models.py': '# Custom user model extending Django AbstractUser\n# Adds role field: admin, teacher, student\n',
    'users/views.py': '# User management views\n# Handles login, logout, create, edit, delete, profile\n',
    'users/urls.py': '# User app URL patterns\n',
    'users/admin.py': '# Register CustomUser model with Django admin panel\n',

    'courses/models.py': '# Course model\n# Each course has a teacher and many enrolled students\n',
    'courses/views.py': '# Course management views\n# Admin can create/edit/delete courses and assign teachers and students\n',
    'courses/urls.py': '# Course app URL patterns\n',
    'courses/admin.py': '# Register Course model with Django admin panel\n',

    'classes/models.py': '# Classroom model\n# Links a course with a teacher and group of students\n',
    'classes/views.py': '# Classroom management views\n# Admin creates classes, assigns teacher and students\n',
    'classes/urls.py': '# Classes app URL patterns\n',
    'classes/admin.py': '# Register Classroom model with Django admin panel\n',

    'attendance/models.py': '# Attendance models\n# AttendanceSession: one per class per date\n# AttendanceRecord: one per student per session\n',
    'attendance/views.py': '# Attendance views\n# Teachers take attendance, view reports and session history\n',
    'attendance/urls.py': '# Attendance app URL patterns\n',
    'attendance/admin.py': '# Register Attendance models with Django admin panel\n',

    'assignments/models.py': '# Assignment and Submission models\n# Teachers upload assignments, students submit, teachers grade\n',
    'assignments/views.py': '# Assignment views\n# Full lifecycle: create, submit, grade, view feedback\n',
    'assignments/urls.py': '# Assignments app URL patterns\n',
    'assignments/admin.py': '# Register Assignment and Submission models with admin panel\n',
}

# ── HTML file comments ────────────────────────────────────────────
html_comments = {
    'templates/base.html': '<!-- Base template - sidebar layout shared by all pages -->',
    'templates/core/dashboard.html': '<!-- Dashboard template - shows different stats per role -->',

    'users/templates/users/login.html': '<!-- Login page - username and password form -->',
    'users/templates/users/user_list.html': '<!-- User list page - shows all users with filter by role -->',
    'users/templates/users/user_form.html': '<!-- User create/edit form -->',
    'users/templates/users/profile.html': '<!-- User profile page - edit own details -->',
    'users/templates/users/confirm_delete.html': '<!-- Confirm delete page for users -->',

    'courses/templates/courses/course_list.html': '<!-- Course list page - shows all courses -->',
    'courses/templates/courses/course_form.html': '<!-- Course create/edit form -->',
    'courses/templates/courses/course_detail.html': '<!-- Course detail page - shows enrolled students and classes -->',
    'courses/templates/courses/confirm_delete.html': '<!-- Confirm delete page for courses -->',

    'classes/templates/classes/class_list.html': '<!-- Class list page - shows all classrooms -->',
    'classes/templates/classes/class_form.html': '<!-- Class create/edit form - assign teacher and students -->',
    'classes/templates/classes/class_detail.html': '<!-- Class detail page - shows students, attendance, assignments -->',
    'classes/templates/classes/confirm_delete.html': '<!-- Confirm delete page for classes -->',

    'attendance/templates/attendance/attendance_list.html': '<!-- Attendance sessions list page -->',
    'attendance/templates/attendance/take_attendance.html': '<!-- Take attendance page - mark present/absent/late per student -->',
    'attendance/templates/attendance/attendance_report.html': '<!-- Attendance report - shows percentage per student -->',
    'attendance/templates/attendance/session_detail.html': '<!-- Single session detail - all student records -->',

    'assignments/templates/assignments/assignment_list.html': '<!-- Assignment list page -->',
    'assignments/templates/assignments/assignment_form.html': '<!-- Assignment create/edit form -->',
    'assignments/templates/assignments/assignment_detail.html': '<!-- Assignment detail - submissions list for teachers -->',
    'assignments/templates/assignments/submit_assignment.html': '<!-- Student assignment submission form -->',
    'assignments/templates/assignments/grade_submission.html': '<!-- Grade submission form for teachers -->',
    'assignments/templates/assignments/confirm_delete.html': '<!-- Confirm delete page for assignments -->',
}

# ── CSS/JS comments ───────────────────────────────────────────────
static_comments = {
    'static/css/main.css': '/* ============================================\n   EduManage College Management System\n   Main Stylesheet\n   Author: Anubhav Rijal & Kishor Kumar Thagunna\n   Description: Custom CSS for layout, sidebar,\n   cards, tables, forms, badges, and responsive design\n   ============================================ */\n',
    'static/js/main.js': '// ============================================\n// EduManage College Management System\n// Main JavaScript File\n// Author: Anubhav Rijal & Kishor Kumar Thagunna\n// Description: Auto-dismiss alerts, active nav,\n// table search, attendance quick-select, form validation\n// ============================================\n',
}

def add_comment_to_file(filepath, comment, mode='prepend'):
    if not os.path.exists(filepath):
        print(f'  SKIP (not found): {filepath}')
        return
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    if comment.strip() in content:
        print(f'  SKIP (already has comment): {filepath}')
        return
    if mode == 'prepend':
        new_content = comment + '\n' + content
    else:
        new_content = content + '\n' + comment
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'  OK: {filepath}')

print('Adding comments to Python files...')
for filepath, comment in python_comments.items():
    add_comment_to_file(filepath, comment)

print('\nAdding comments to HTML files...')
for filepath, comment in html_comments.items():
    add_comment_to_file(filepath, comment)

print('\nAdding comments to CSS/JS files...')
for filepath, comment in static_comments.items():
    add_comment_to_file(filepath, comment)

print('\nDone! All comments added.')