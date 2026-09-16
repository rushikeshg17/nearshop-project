/**
 * NearShop — Leaflet.js Map Module
 * Initializes the shop map, adds markers with popups, and exposes
 * highlightShopMarker() for syncing with search result cards.
 */

const NS_MAP = (function () {
  let _map = null;
  const _markers = {}; // shopId → L.Marker

  // Custom blue marker icon
  function shopIcon(color = '#1a56db') {
    return L.divIcon({
      className: '',
      html: `<div style="
        background:${color};
        width:36px;height:36px;border-radius:50% 50% 50% 0;
        transform:rotate(-45deg);border:3px solid #fff;
        box-shadow:0 3px 10px rgba(0,0,0,.25);">
        <i class='bi bi-shop' style='display:block;transform:rotate(45deg);text-align:center;line-height:30px;font-size:14px;color:#fff;'></i>
      </div>`,
      iconSize: [36, 36],
      iconAnchor: [18, 36],
      popupAnchor: [0, -40],
    });
  }

  function userIcon() {
    return L.divIcon({
      className: '',
      html: `<div style="
        background:#16a34a;width:18px;height:18px;border-radius:50%;
        border:3px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.25);">
      </div>`,
      iconSize: [18, 18],
      iconAnchor: [9, 9],
    });
  }

  function buildPopup(shop) {
    const products = (shop.products || []).slice(0, 3)
      .map(p => `<div style="display:flex;justify-content:space-between;font-size:12px;padding:2px 0;border-bottom:1px solid #f1f5f9;">
        <span>${p.name}</span>
        <strong style="color:#16a34a;">₹${p.price}</strong>
      </div>`).join('');

    const mapsUrl = `https://maps.google.com?q=${shop.lat},${shop.lng}`;
    const badge   = `<span style="background:#dbeafe;color:#1d4ed8;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600;">${shop.category || ''}</span>`;

    return `<div style="min-width:200px;font-family:'Inter',system-ui,sans-serif;">
      <div style="font-size:14px;font-weight:700;color:#0f172a;margin-bottom:4px;">${shop.name}</div>
      ${badge}
      <div style="font-size:12px;color:#64748b;margin:6px 0;">
        <i class='bi bi-geo-alt'></i> ${shop.address || ''}
      </div>
      ${products ? `<div style="margin:8px 0 6px;font-size:11px;font-weight:600;text-transform:uppercase;color:#94a3b8;">In Stock</div>${products}` : ''}
      <div style="display:flex;gap:6px;margin-top:10px;">
        <a href="${mapsUrl}" target="_blank"
           style="flex:1;background:#1a56db;color:#fff;text-align:center;padding:6px;border-radius:6px;font-size:12px;font-weight:600;text-decoration:none;">
          <i class='bi bi-signpost'></i> Directions
        </a>
        <a href="/search?q=${encodeURIComponent(shop.name)}"
           style="flex:1;background:#f1f5f9;color:#0f172a;text-align:center;padding:6px;border-radius:6px;font-size:12px;font-weight:600;text-decoration:none;">
          <i class='bi bi-search'></i> Products
        </a>
      </div>
    </div>`;
  }

  function initMap(containerId, shops, userLat, userLng) {
    const el = document.getElementById(containerId);
    if (!el) return;

    const centerLat = (userLat && userLat !== 0) ? userLat : 15.1394;
    const centerLng = (userLng && userLng !== 0) ? userLng : 76.9214;

    // Destroy existing map instance if re-initialising
    if (_map) {
      _map.remove();
      _map = null;
    }

    _map = L.map(containerId, { zoomControl: false }).setView([centerLat, centerLng], 14);

    // Tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(_map);

    // Custom zoom controls
    L.control.zoom({ position: 'bottomright' }).addTo(_map);

    // User location marker
    if (userLat && userLng) {
      L.marker([userLat, userLng], { icon: userIcon() })
        .addTo(_map)
        .bindPopup('<strong>Your Location</strong>');
    }

    // Shop markers
    const bounds = [];
    shops.forEach(shop => {
      if (!shop.lat || !shop.lng) return;
      const marker = L.marker([shop.lat, shop.lng], { icon: shopIcon() })
        .addTo(_map)
        .bindPopup(buildPopup(shop), { maxWidth: 240 });
      _markers[shop.id] = marker;
      bounds.push([shop.lat, shop.lng]);
    });

    // Fit map to markers
    if (bounds.length > 0) {
      try {
        _map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 });
      } catch (e) {}
    }

    // Scale control
    L.control.scale({ imperial: false }).addTo(_map);
  }

  function highlightShopMarker(shopId) {
    if (!_map || !_markers[shopId]) return;
    // Reset all markers
    Object.values(_markers).forEach(m => {
      m.setIcon(shopIcon('#1a56db'));
    });
    // Highlight the selected one
    const marker = _markers[shopId];
    marker.setIcon(shopIcon('#16a34a'));
    _map.panTo(marker.getLatLng(), { animate: true, duration: 0.5 });
    marker.openPopup();
  }

  function addUserLocationMarker(lat, lng) {
    if (!_map) return;
    L.marker([lat, lng], { icon: userIcon() })
      .addTo(_map)
      .bindPopup('<strong>You are here</strong>')
      .openPopup();
    _map.setView([lat, lng], 15);
  }

  // Public API
  return { initMap, highlightShopMarker, addUserLocationMarker };
})();

// Expose globally
window.initMap             = NS_MAP.initMap;
window.highlightShopMarker = NS_MAP.highlightShopMarker;
window.addUserLocationMarker = NS_MAP.addUserLocationMarker;
