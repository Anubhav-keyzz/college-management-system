# Classroom model
# Links a course with a teacher and group of students

"""
classes/models.py — Classroom model for the College Management System.

A Classroom represents a section of a Course taught by a specific teacher
to a specific set of students. One Course can have multiple Classrooms
(e.g., "CS101 - Section A" and "CS101 - Section B").
"""

from django.db import models       # Django ORM field types
from users.models import CustomUser   # FK to our custom user model
from courses.models import Course     # FK to the Course this class belongs to


class Classroom(models.Model):
    """
    Represents a physical/virtual class section of a Course.

    Fields:
      name        — display name, e.g. "Year 2 - Section A"
      section     — optional section label, e.g. "A", "Morning"
      course      — the Course this classroom belongs to (CASCADE delete)
      teacher     — the teacher assigned to this classroom (nullable)
      students    — enrolled students (ManyToMany)
      schedule    — optional free-text schedule info, e.g. "Mon/Wed 10:00"
      room_number — optional room identifier, e.g. "Lab 3"
      created_at  — auto-set creation timestamp
    """

    # Human-readable name for this class section
    name = models.CharField(max_length=100)

    # Optional section label (e.g. "A", "B", "Evening")
    section = models.CharField(max_length=20, blank=True)

    # The course this classroom is a section of.
    # CASCADE: deleting a course also deletes all its classrooms.
    # related_name allows: course.classrooms.all()
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='classrooms',
    )

    # Teacher assigned to this classroom.
    # SET_NULL: if the teacher is deleted, the classroom still exists (teacher=None).
    # limit_choices_to restricts to users with role='teacher'.
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='teaching_classes',
        limit_choices_to={'role': 'teacher'},
    )

    # Students enrolled in this classroom.
    # related_name allows: student.enrolled_classes.all()
    students = models.ManyToManyField(
        CustomUser,
        blank=True,
        related_name='enrolled_classes',
        limit_choices_to={'role': 'student'},
    )

    # Free-text schedule description (e.g. "Mon / Wed 10:00–11:30")
    schedule = models.CharField(max_length=200, blank=True)

    # Physical or virtual room identifier
    room_number = models.CharField(max_length=20, blank=True)

    # Automatically recorded when the classroom record is first saved
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Display as 'Classroom Name - COURSE_CODE', e.g. 'Year 2A - CS101'."""
        return f"{self.name} - {self.course.code}"

    class Meta:
        # Default ordering: alphabetically by classroom name
        ordering = ['name']
