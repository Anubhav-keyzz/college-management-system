# Assignment and Submission models
# Teachers upload assignments, students submit, teachers grade

"""
assignments/models.py — Models for assignments and student submissions.

Two models:
  Assignment           — a task posted by a teacher to a classroom
  AssignmentSubmission — a student's response (file and/or text) to an assignment
"""

from django.db import models       # Django ORM field types
from users.models import CustomUser   # FK to our custom user model
from classes.models import Classroom  # FK to Classroom model


class Assignment(models.Model):
    """
    Represents an assignment posted by a teacher for a classroom.

    Fields:
      title       — short title of the assignment
      description — optional detailed instructions
      classroom   — the classroom this assignment belongs to
      uploaded_by — the teacher/admin who created it
      file        — optional file attachment (e.g. PDF instructions)
      due_date    — optional submission deadline
      max_marks   — maximum marks for grading (default 100)
      created_at  — auto-set creation timestamp
    """

    # Short title visible in lists (e.g. "Week 3 Lab Report")
    title = models.CharField(max_length=200)

    # Optional detailed description or instructions
    description = models.TextField(blank=True)

    # The classroom this assignment is posted to.
    # CASCADE: deleting a classroom removes all its assignments.
    # related_name allows: classroom.assignments.all()
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name='assignments',
    )

    # The teacher (or admin) who created this assignment.
    # CASCADE: if the creator's account is deleted, their assignments are also deleted.
    # related_name allows: user.created_assignments.all()
    uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='created_assignments',
    )

    # Optional downloadable file for students (e.g. a question sheet PDF)
    # Uploaded files are stored under MEDIA_ROOT/assignments/
    file = models.FileField(upload_to='assignments/', blank=True, null=True)

    # Optional deadline; null means no deadline set
    due_date = models.DateTimeField(null=True, blank=True)

    # Maximum achievable marks; used for grading submissions
    max_marks = models.PositiveIntegerField(default=100)

    # Automatically set when the assignment is first created
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Show most recently created assignments first
        ordering = ['-created_at']

    def __str__(self):
        """Display as 'Title (Classroom Name - COURSE_CODE)'."""
        return f"{self.title} ({self.classroom})"


class AssignmentSubmission(models.Model):
    """
    Represents a student's submission for an Assignment.

    A student can submit at most one response per assignment
    (enforced by unique_together). Submissions may include a file,
    text, or both.

    Fields:
      assignment   — the assignment being answered
      student      — the student who submitted
      file         — optional uploaded file (e.g. completed PDF)
      text         — optional text answer
      submitted_at — auto-set timestamp
      marks        — marks awarded after grading (null until graded)
      feedback     — optional teacher feedback text
      is_graded    — flag set to True once the teacher has graded it
    """

    # The assignment this submission is a response to.
    # CASCADE: deleting an assignment removes all its submissions.
    # related_name allows: assignment.submissions.all()
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
    )

    # The student who submitted.
    # CASCADE: deleting the student account deletes their submissions.
    # limit_choices_to: only student-role users can appear in admin.
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
    )

    # Optional file upload from the student (stored under MEDIA_ROOT/submissions/)
    file = models.FileField(upload_to='submissions/', blank=True, null=True)

    # Optional text answer (e.g. for short-answer assignments)
    text = models.TextField(blank=True)

    # Automatically set to now when the submission is first created
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Marks awarded by the teacher (null = not yet graded)
    marks = models.PositiveIntegerField(null=True, blank=True)

    # Teacher's written feedback on the submission
    feedback = models.TextField(blank=True)

    # True once marks and/or feedback have been saved by a teacher
    is_graded = models.BooleanField(default=False)

    class Meta:
        # Each student may only have one submission per assignment
        unique_together = ['assignment', 'student']

    def __str__(self):
        """Display as 'Student Name - Assignment Title'."""
        return f"{self.student} - {self.assignment.title}"
