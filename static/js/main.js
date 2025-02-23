// College Management System - Main JS

document.addEventListener('DOMContentLoaded', function () {

  // ── Auto-dismiss alerts ──────────────────────────────────
  document.querySelectorAll('.alert').forEach(function (el) {
    setTimeout(function () {
      el.style.opacity = '0';
      el.style.transform = 'translateY(-8px)';
      el.style.transition = 'all .4s';
      setTimeout(function () { el.remove(); }, 400);
    }, 4000);
  });

  // ── Active nav link ──────────────────────────────────────
  var path = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(function (link) {
    if (
      link.getAttribute('href') &&
      path.startsWith(link.getAttribute('href')) &&
      link.getAttribute('href') !== '/'
    ) {
      link.classList.add('active');
    }
  });

  // ── Mobile sidebar toggle (with overlay) ────────────────
  var toggleBtn = document.getElementById('sidebar-toggle');
  var sidebar   = document.querySelector('.sidebar');
  var overlay   = document.getElementById('sidebar-overlay');

  function openSidebar() {
    sidebar.classList.add('open');
    if (overlay) overlay.classList.add('show');
    document.body.style.overflow = 'hidden'; // prevent background scroll
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('show');
    document.body.style.overflow = '';
  }

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      if (sidebar.classList.contains('open')) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });
  }

  // Close sidebar when clicking the overlay
  if (overlay) {
    overlay.addEventListener('click', closeSidebar);
  }

  // Close sidebar when a nav link is clicked (mobile UX)
  if (sidebar) {
    sidebar.querySelectorAll('.nav-item').forEach(function (link) {
      link.addEventListener('click', function () {
        if (window.innerWidth <= 768) {
          closeSidebar();
        }
      });
    });
  }

  // Close sidebar on window resize back to desktop
  window.addEventListener('resize', function () {
    if (window.innerWidth > 768) {
      closeSidebar();
    }
  });

  // ── Confirm delete ───────────────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      if (!confirm(el.dataset.confirm || 'Are you sure?')) {
        e.preventDefault();
      }
    });
  });

  // ── Select All / Deselect All for multi-select ───────────
  document.querySelectorAll('[data-select-all]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var target = document.querySelector(btn.dataset.selectAll);
      if (target) {
        Array.from(target.options).forEach(function (opt) { opt.selected = true; });
      }
    });
  });
  document.querySelectorAll('[data-deselect-all]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var target = document.querySelector(btn.dataset.deselectAll);
      if (target) {
        Array.from(target.options).forEach(function (opt) { opt.selected = false; });
      }
    });
  });

  // ── Date picker default today ────────────────────────────
  document.querySelectorAll('input[type=date][data-today]').forEach(function (el) {
    if (!el.value) {
      el.value = new Date().toISOString().split('T')[0];
    }
  });

  // ── Progress bar animation ───────────────────────────────
  document.querySelectorAll('.progress-bar[data-width]').forEach(function (bar) {
    var w = parseFloat(bar.dataset.width) || 0;
    bar.style.width = '0%';
    setTimeout(function () { bar.style.width = w + '%'; }, 100);
    if (w >= 75)      bar.classList.add('green');
    else if (w >= 50) bar.classList.add('orange');
    else              bar.classList.add('red');
  });

  // ── Fee payment amount validation ────────────────────────
  var payInput   = document.getElementById('pay-amount');
  var maxBalance = document.getElementById('max-balance');
  if (payInput && maxBalance) {
    payInput.addEventListener('input', function () {
      var max = parseFloat(maxBalance.value);
      if (parseFloat(payInput.value) > max) {
        payInput.value = max;
      }
    });
    payInput.setAttribute('max', maxBalance.value);
  }

  // ── Attendance: mark all present / absent ────────────────
  var allPresent = document.getElementById('mark-all-present');
  var allAbsent  = document.getElementById('mark-all-absent');
  if (allPresent) {
    allPresent.addEventListener('click', function () {
      document.querySelectorAll('input[type=radio][value=present]').forEach(function (r) { r.checked = true; });
    });
  }
  if (allAbsent) {
    allAbsent.addEventListener('click', function () {
      document.querySelectorAll('input[type=radio][value=absent]').forEach(function (r) { r.checked = true; });
    });
  }

  // ── Table search ─────────────────────────────────────────
  var searchInput = document.getElementById('table-search');
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      var q = searchInput.value.toLowerCase();
      document.querySelectorAll('tbody tr').forEach(function (row) {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }

  // ── File size validator (500 KB limit for submissions) ───
  var fileInputs = document.querySelectorAll('input[type=file]');
  fileInputs.forEach(function (input) {
    input.addEventListener('change', function () {
      var maxKB  = 500;
      var maxBytes = maxKB * 1024;
      if (input.files && input.files[0]) {
        if (input.files[0].size > maxBytes) {
          alert(
            'File is too large!\n' +
            'Your file: ' + Math.round(input.files[0].size / 1024) + ' KB\n' +
            'Maximum allowed: ' + maxKB + ' KB\n\n' +
            'Please choose a smaller file.'
          );
          input.value = ''; // clear the selection
        }
      }
    });
  });

});