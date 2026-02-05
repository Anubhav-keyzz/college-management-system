# Course model
# Each course has a teacher and many enrolled students

"""
courses/models.py — Course model for the College Management System.

A Course represents a subject being offered (e.g., "Mathematics", "CS101").
Each course may be assigned to one teacher and enrolled by many students.
"""

from django.db import models      # Django ORM field types
from users.models import CustomUser  # Our custom user model


class Course(models.Model):
    """
    Represents an academic course.

    Fields:
      name        — full descriptive name, e.g. "Introduction to Python"
      code        — short unique identifier, e.g. "CS101"
      description — optional longer description of course content
      credits     — academic credit hours (default 3)
      teacher     — the teacher responsible for this course (nullable)
      students    — many-to-many relationship with enrolled students
      created_at  — auto-set timestamp when the course was created
    """

    # Full course name (e.g. "Data Structures and Algorithms")
    name = models.CharField(max_length=200)

    # Unique short code used for identification (e.g. "DSA301")
    code = models.CharField(max_length=20, unique=True)

    # Optional course syllabus / description
    description = models.TextField(blank=True)

    # Number of academic credits this course is worth
    credits = models.PositiveIntegerField(default=3)

    # The teacher who teaches this course.
    # SET_NULL means if the teacher is deleted, the course still exists.
    # limit_choices_to restricts the FK dropdown to users with role='teacher'.
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='teaching_courses',          # Access via: teacher.teaching_courses.all()
        limit_choices_to={'role': 'teacher'},     # Only teacher users appear in admin
    )

    # Students enrolled in this course (many students can enroll in many courses)
    # related_name allows: student.enrolled_courses.all()
    students = models.ManyToManyField(
        CustomUser,
        blank=True,
        related_name='enrolled_courses',
        limit_choices_to={'role': 'student'},
    )

    # Automatically set to the current date/time when the record is first created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Display as 'CODE - Name', e.g. 'CS101 - Introduction to Python'."""
        return f"{self.code} - {self.name}"
