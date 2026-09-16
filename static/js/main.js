/**
 * NearShop — Main JS
 * Handles: flash auto-dismiss, sidebar toggle, image preview,
 *          quick stock update, search autocomplete, form validation
 */

document.addEventListener('DOMContentLoaded', function () {

  // ── Flash message auto-dismiss ──────────────────────────────────
  document.querySelectorAll('[data-auto-dismiss]').forEach(el => {
    setTimeout(() => {
      if (el) {
        el.style.opacity = '0';
        el.style.transition = 'opacity .4s';
        setTimeout(() => el.remove(), 400);
      }
    }, 4000);
  });

  // ── Sidebar mobile toggle ───────────────────────────────────────
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar       = document.getElementById('dashboardSidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('show');
    });
  }

  // ── Image preview on file input ─────────────────────────────────
  document.querySelectorAll('input[type="file"][data-preview]').forEach(input => {
    input.addEventListener('change', function () {
      const previewId = this.dataset.preview;
      const preview   = document.getElementById(previewId);
      if (preview && this.files && this.files[0]) {
        const reader = new FileReader();
        reader.onload = e => {
          preview.src = e.target.result;
          preview.style.display = 'block';
        };
        reader.readAsDataURL(this.files[0]);
      }
    });
  });

  // ── Quick stock inline update ───────────────────────────────────
  document.querySelectorAll('.qty-display').forEach(span => {
    span.addEventListener('click', function () {
      const productId = this.dataset.productId;
      const current   = parseInt(this.textContent);
      const input     = document.createElement('input');
      input.type      = 'number';
      input.value     = current;
      input.min       = 0;
      input.className = 'form-control form-control-sm d-inline-block';
      input.style.width = '80px';

      const saveBtn = document.createElement('button');
      saveBtn.textContent = '✓';
      saveBtn.className   = 'btn btn-sm btn-success ms-1';

      const cancel = document.createElement('button');
      cancel.textContent = '✕';
      cancel.className   = 'btn btn-sm btn-outline-secondary ms-1';

      const wrapper = document.createElement('span');
      wrapper.append(input, saveBtn, cancel);
      this.replaceWith(wrapper);

      const restore = (val) => {
        const newSpan = document.createElement('span');
        newSpan.className = 'qty-display';
        newSpan.dataset.productId = productId;
        newSpan.textContent = val;
        wrapper.replaceWith(newSpan);
        // Re-bind the new span
        newSpan.addEventListener('click', arguments.callee);
      };

      saveBtn.addEventListener('click', () => {
        const qty = parseInt(input.value);
        if (isNaN(qty) || qty < 0) return;
        fetch(`/api/products/${productId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ quantity: qty }),
        })
          .then(r => r.json())
          .then(data => {
            if (data.success) {
              showToast(`Stock updated to ${qty}`, 'success');
              location.reload(); // Refresh to update badges
            } else {
              showToast('Update failed', 'danger');
              restore(current);
            }
          })
          .catch(() => { showToast('Network error', 'danger'); restore(current); });
      });
      cancel.addEventListener('click', () => restore(current));
      input.focus();
    });
  });

  // ── Delete product confirmation ─────────────────────────────────
  document.querySelectorAll('[data-confirm-delete]').forEach(btn => {
    btn.addEventListener('click', function (e) {
      const name = this.dataset.productName || 'this product';
      if (!confirm(`Delete "${name}"? This cannot be undone.`)) {
        e.preventDefault();
      }
    });
  });

  // ── Edit product modal pre-fill ─────────────────────────────────
  document.querySelectorAll('[data-edit-product]').forEach(btn => {
    btn.addEventListener('click', function () {
      const modal = document.getElementById('editProductModal');
      if (!modal) return;
      const data = this.dataset;
      modal.querySelector('[name=product_name]').value = data.name  || '';
      modal.querySelector('[name=category]').value     = data.cat   || '';
      modal.querySelector('[name=price]').value        = data.price || '';
      modal.querySelector('[name=quantity]').value     = data.qty   || '';
      modal.querySelector('[name=brand]').value        = data.brand || '';
      modal.querySelector('[name=description]').value  = data.desc  || '';
      modal.querySelector('form').action = `/api/products/${data.id}`;
      const prev = modal.querySelector('#editImgPreview');
      if (prev) {
        prev.src = `/static/images/products/${data.image || 'default.png'}`;
        prev.style.display = 'block';
      }
    });
  });

  // ── Client-side product table search ───────────────────────────
  const tableSearch = document.getElementById('tableSearchInput');
  if (tableSearch) {
    tableSearch.addEventListener('input', function () {
      const q = this.value.toLowerCase();
      document.querySelectorAll('.product-row').forEach(row => {
        const text = row.dataset.searchText || row.textContent;
        row.style.display = text.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }



  // ── Generic search autocomplete (non-hero) ──────────────────────
  setupAutocomplete('searchInput', 'searchDropdown');

  // ── Bootstrap tooltips init ────────────────────────────────────
  const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipEls.forEach(el => new bootstrap.Tooltip(el));
});

// ────────────────────────────────────────────────────────────────
// Helpers
// ────────────────────────────────────────────────────────────────

function setupAutocomplete(inputId, dropdownId) {
  const input    = document.getElementById(inputId);
  const dropdown = document.getElementById(dropdownId);
  if (!input || !dropdown) return;

  let timer;
  input.addEventListener('input', function () {
    clearTimeout(timer);
    const q = this.value.trim();
    if (q.length < 2) { dropdown.style.display = 'none'; return; }
    timer = setTimeout(() => {
      fetch(`/api/autocomplete?q=${encodeURIComponent(q)}`)
        .then(r => r.json())
        .then(data => {
          if (!data.length) { dropdown.style.display = 'none'; return; }
          dropdown.innerHTML = data.map(s =>
            `<div class="ac-item" onclick="document.getElementById('${inputId}').value='${s}';
              document.getElementById('${dropdownId}').style.display='none';">
              <i class="bi bi-search text-muted" style="font-size:.8rem;"></i> ${s}
            </div>`
          ).join('');
          dropdown.style.display = 'block';
        })
        .catch(() => {});
    }, 250);
  });

  document.addEventListener('click', e => {
    if (e.target !== input) dropdown.style.display = 'none';
  });
}

function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `alert alert-${type} alert-dismissible fade show shadow`;
  toast.style.cssText = 'position:fixed;top:80px;right:1rem;z-index:9999;min-width:260px;';
  toast.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity .4s';
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

// Copy to clipboard
function copyToClipboard(text, btnEl) {
  navigator.clipboard.writeText(text).then(() => {
    const orig = btnEl.innerHTML;
    btnEl.innerHTML = '<i class="bi bi-check"></i> Copied!';
    btnEl.classList.add('btn-success');
    btnEl.classList.remove('btn-outline-secondary');
    setTimeout(() => {
      btnEl.innerHTML = orig;
      btnEl.classList.remove('btn-success');
      btnEl.classList.add('btn-outline-secondary');
    }, 2000);
  });
}
