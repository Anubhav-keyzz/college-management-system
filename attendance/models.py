# Attendance models
# AttendanceSession: one per class per date
# AttendanceRecord: one per student per session

"""
attendance/models.py — Models for tracking student attendance.

Two models work together:
  AttendanceSession — one session per classroom per date (e.g. "CS101 on 2026-03-27")
  AttendanceRecord  — one record per student per session (present / absent / late)
"""

from django.db import models      # Django ORM field types
from users.models import CustomUser  # FK to our custom user model
from classes.models import Classroom # FK to Classroom model


class AttendanceSession(models.Model):
    """
    Represents a single attendance-taking event for one classroom on one date.

    The unique_together constraint ensures attendance can only be taken once
    per classroom per calendar date (no duplicate sessions).

    Fields:
      classroom  — which classroom this session belongs to
      date       — the date attendance was taken
      taken_by   — the teacher who took attendance (nullable — teacher may be deleted)
      created_at — auto-set timestamp
    """

    # The classroom whose attendance is being recorded
    # CASCADE: if the classroom is deleted, all its sessions are also deleted
    # related_name allows: classroom.sessions.all()
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name='sessions',
    )

    # Calendar date for this attendance session
    date = models.DateField()

    # Teacher who recorded attendance.
    # SET_NULL: if the teacher account is deleted, the session record is kept.
    # limit_choices_to: only teacher-role users appear in the admin dropdown.
    taken_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'teacher'},
    )

    # Auto-set to now when the session record is first created
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent duplicate sessions: one per classroom per day
        unique_together = ['classroom', 'date']
        # Show most recent sessions first by default
        ordering = ['-date']

    def __str__(self):
        """Display as 'Classroom Name - YYYY-MM-DD'."""
        return f"{self.classroom} - {self.date}"


class AttendanceRecord(models.Model):
    """
    Records one student's attendance status for a specific session.

    The unique_together constraint prevents a student being recorded twice
    in the same session.

    Fields:
      session — which attendance session this record belongs to
      student — the student being recorded
      status  — 'present', 'absent', or 'late'
      note    — optional free-text note (e.g. "doctor's appointment")
    """

    # Valid status options shown in the template radio buttons and stored in DB
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent',  'Absent'),
        ('late',    'Late'),
    ]

    # The session this record belongs to.
    # CASCADE: deleting a session removes all its attendance records.
    # related_name allows: session.records.all()
    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name='records',
    )

    # The student whose attendance is being recorded.
    # CASCADE: if the student account is deleted, their records are deleted too.
    # limit_choices_to: only student-role users can appear here.
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
    )

    # The attendance status — defaults to 'absent' as a safe fallback
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='absent',
    )

    # Optional note explaining absence or lateness
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        # Each student can only have one record per session
        unique_together = ['session', 'student']

    def __str__(self):
        """Display as 'Student Name - status'."""
        return f"{self.student} - {self.status}"
