# Core app models - no models needed here

# core/models.py — No models are defined in the core app.
#
# The core app exists purely for shared functionality:
#   - Dashboard view  (core/views.py)
#   - Login / logout  (re-exported from users/views.py via core/urls.py)
#   - Excel export    (core/views.py → export_excel)
#   - PDF export      (core/views.py → export_pdf)
#
# All data models live in the other apps (users, courses, classes,
# attendance, assignments).
