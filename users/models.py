# Custom user model extending Django AbstractUser
# Adds role field: admin, teacher, student

"""
users/models.py — Custom user model for the College Management System.

Instead of Django's built-in User, we extend AbstractUser so we can add
extra fields (role, phone, address, date_of_birth) while keeping all
built-in auth features (password hashing, session support, permissions).
"""

from django.contrib.auth.models import AbstractUser  # Base user model with auth features
from django.db import models                         # Django ORM field types


class CustomUser(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.

    Three roles are supported:
      - admin   : full access to all CMS features
      - teacher : manages courses, classes, assignments, attendance
      - student : views content, submits assignments, sees own attendance
    """

    # ── Role choices ──────────────────────────────────────────────────────────
    ROLE_CHOICES = [
        ('admin',   'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]

    # Role field — determines what each user can see and do in the CMS
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',  # New users are students by default
    )

    # Optional contact / profile fields (all can be left blank)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        """Human-readable representation: 'Full Name (role)' or 'username (role)'."""
        return f"{self.get_full_name() or self.username} ({self.role})"

    # ── Convenience role-check properties ─────────────────────────────────────
    # These allow clean role checks in views/templates: user.is_admin, etc.

    @property
    def is_admin(self):
        """Return True if this user has the 'admin' role."""
        return self.role == 'admin'

    @property
    def is_teacher(self):
        """Return True if this user has the 'teacher' role."""
        return self.role == 'teacher'

    @property
    def is_student(self):
        """Return True if this user has the 'student' role."""
        return self.role == 'student'
