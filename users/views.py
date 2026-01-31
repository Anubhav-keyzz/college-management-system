# User management views
# Handles login, logout, create, edit, delete, profile

"""
users/views.py — Views for authentication and user management.

Handles:
  - Login / logout
  - User list (admin only)
  - Create / edit / delete users (admin only)
  - User's own profile page
"""

from django.shortcuts import render, redirect, get_object_or_404  # Rendering & redirects
from django.contrib.auth import login, logout, authenticate       # Auth helpers
from django.contrib.auth.decorators import login_required         # Redirect unauthenticated users
from django.contrib import messages                               # Flash messages
from .models import CustomUser                                    # Our custom user model


# ─── Authentication ──────────────────────────────────────────────────────────

def login_view(request):
    """
    Display the login form (GET) and authenticate the user (POST).

    - If the user is already authenticated, redirect straight to the dashboard.
    - On POST, authenticate with username/password. On success, log the user in
      and redirect to dashboard. On failure, show an error flash message.
    """
    # Already logged in — no need to show the login page
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        # Attempt to authenticate with the submitted credentials
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password'),
        )
        if user:
            # Credentials valid — create a session and redirect
            login(request, user)
            return redirect('dashboard')
        # Credentials invalid — inform the user
        messages.error(request, 'Invalid credentials.')

    # Render the login form for GET requests (or failed POST)
    return render(request, 'users/login.html')


def logout_view(request):
    """
    Log the current user out and redirect to the login page.
    No template needed — just clear the session and redirect.
    """
    logout(request)
    return redirect('login')


# ─── User Management (admin only) ────────────────────────────────────────────

@login_required
def user_list(request):
    """
    Display a list of all users, excluding the currently logged-in admin.

    Supports optional role-based filtering via ?role=student|teacher|admin.
    Only admins can access this view; others are redirected to the dashboard.
    """
    # Restrict access to admins
    if not request.user.is_admin:
        return redirect('dashboard')

    # Read optional role filter from the query string (e.g., ?role=student)
    role = request.GET.get('role', '')

    # Exclude the current admin from the list to avoid self-deletion accidents
    users = CustomUser.objects.exclude(pk=request.user.pk)

    # Apply role filter if one was provided
    if role:
        users = users.filter(role=role)

    return render(request, 'users/user_list.html', {'users': users, 'role_filter': role})


@login_required
def create_user(request):
    """
    Create a new CMS user (admin only).

    Validates that:
      - Passwords match
      - Username is not already taken
    Then creates the user with a properly hashed password.
    """
    # Only admins may create users
    if not request.user.is_admin:
        return redirect('dashboard')

    if request.method == 'POST':
        p = request.POST  # Shorthand for the POST data dictionary

        # ── Validation ────────────────────────────────────────────────────────
        if p.get('password') != p.get('confirm_password'):
            messages.error(request, 'Passwords do not match.')
        elif CustomUser.objects.filter(username=p['username']).exists():
            messages.error(request, 'Username already exists.')
        else:
            # ── Create the user object ─────────────────────────────────────
            u = CustomUser(
                username=p['username'],
                first_name=p.get('first_name', ''),
                last_name=p.get('last_name', ''),
                email=p.get('email', ''),
                role=p['role'],
                phone=p.get('phone', ''),
                address=p.get('address', ''),
            )
            # Set date_of_birth only if provided (it's optional)
            if p.get('date_of_birth'):
                u.date_of_birth = p['date_of_birth']

            # Hash the password using Django's built-in hasher
            u.set_password(p['password'])
            u.save()

            messages.success(request, f"User '{u.username}' created!")
            return redirect('user_list')

    # Render the empty creation form for GET requests
    return render(request, 'users/user_form.html', {
        'title': 'Create User',
        'action': 'Create',
    })


@login_required
def edit_user(request, pk):
    """
    Edit an existing user's details (admin only).

    If a new password is provided in the POST data, it is re-hashed and saved.
    Otherwise, the existing password is kept unchanged.
    """
    # Only admins may edit users
    if not request.user.is_admin:
        return redirect('dashboard')

    # Fetch the user to edit, or return 404 if not found
    u = get_object_or_404(CustomUser, pk=pk)

    if request.method == 'POST':
        p = request.POST

        # Update basic profile fields
        u.first_name = p.get('first_name', '')
        u.last_name  = p.get('last_name', '')
        u.email      = p.get('email', '')
        u.role       = p.get('role', u.role)  # Keep existing role if not submitted
        u.phone      = p.get('phone', '')
        u.address    = p.get('address', '')

        if p.get('date_of_birth'):
            u.date_of_birth = p['date_of_birth']

        # Only update password if the admin explicitly provided a new one
        if p.get('password'):
            u.set_password(p['password'])

        u.save()
        messages.success(request, 'User updated!')
        return redirect('user_list')

    # Render the pre-filled edit form for GET requests
    return render(request, 'users/user_form.html', {
        'title': 'Edit User',
        'action': 'Update',
        'user_obj': u,  # Pass as 'user_obj' to avoid shadowing template's 'user' variable
    })


@login_required
def delete_user(request, pk):
    """
    Delete a user (admin only).

    GET  → Show confirmation page.
    POST → Perform deletion and redirect to user list.
    """
    # Only admins may delete users
    if not request.user.is_admin:
        return redirect('dashboard')

    u = get_object_or_404(CustomUser, pk=pk)

    if request.method == 'POST':
        u.delete()
        messages.success(request, 'User deleted.')
        return redirect('user_list')

    # Show confirmation page before deleting
    return render(request, 'users/confirm_delete.html', {
        'obj': u,
        'cancel_url': 'user_list',  # URL name to redirect on cancel
    })


# ─── Profile (any authenticated user) ────────────────────────────────────────

@login_required
def profile(request):
    """
    Allow any authenticated user to view and update their own profile.

    If a new password is submitted, update_session_auth_hash() is called to
    keep the user logged in after the password change (Django invalidates the
    session on password change by default).
    """
    u = request.user  # The currently logged-in user

    if request.method == 'POST':
        p = request.POST

        # Update editable profile fields
        u.first_name = p.get('first_name', '')
        u.last_name  = p.get('last_name', '')
        u.email      = p.get('email', '')
        u.phone      = p.get('phone', '')
        u.address    = p.get('address', '')

        if p.get('date_of_birth'):
            u.date_of_birth = p['date_of_birth']

        if p.get('password'):
            # Change password and re-anchor the session so the user stays logged in
            u.set_password(p['password'])
            u.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, u)  # Prevent session invalidation
        else:
            # No password change — just save the updated fields
            u.save()

        messages.success(request, 'Profile updated!')
        return redirect('profile')

    # Render the profile page with current user data
    return render(request, 'users/profile.html', {'user_obj': u})
