"""
NearShop — Search Routes
AI-powered product search using Word2Vec semantic expansion.
Includes product detail page with Apriori recommendations + price anomaly alerts.
"""
import math
import datetime
from flask import (Blueprint, render_template, request,
                   jsonify, session, g)
from database.db import get_db
from config import Config

search_bp = Blueprint('search', __name__)


# ──────────────────────────────────────────────────────────────────────────────
# Geo helpers
# ──────────────────────────────────────────────────────────────────────────────

def haversine(lat1, lon1, lat2, lon2):
    """Return distance in km between two lat/lng points."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ──────────────────────────────────────────────────────────────────────────────
# Search Page
# ──────────────────────────────────────────────────────────────────────────────

@search_bp.route('/search')
def search():
    query      = request.args.get('q', '').strip()
    category   = request.args.get('category', '')
    min_price  = request.args.get('min_price', 0, type=float)
    max_price  = request.args.get('max_price', 100000, type=float)
    distance   = request.args.get('distance', 10, type=float)
    sort_by    = request.args.get('sort', 'relevance')
    user_lat   = request.args.get('lat', Config.DEFAULT_LAT, type=float)
    user_lng   = request.args.get('lng', Config.DEFAULT_LNG, type=float)

    results    = []
    shops_map  = []
    recommendations = []

    db = get_db()
    params = []
    where_clauses = ['p.quantity > 0']

    # 1. Query with Word2Vec expansion
    if query:
        try:
            from models.word2vec import get_query_expansion
            expanded_terms = get_query_expansion(query)
        except Exception:
            expanded_terms = query.lower().split()
        expanded_terms = list(set(expanded_terms + query.lower().split()))

        like_conditions = ' OR '.join(
            ['LOWER(p.product_name) LIKE ? OR LOWER(p.description) LIKE ? OR LOWER(p.brand) LIKE ?']
            * len(expanded_terms)
        )
        for term in expanded_terms:
            params.extend([f'%{term}%', f'%{term}%', f'%{term}%'])
        where_clauses.append(f'({like_conditions})')

    # 2. Category filter
    if category:
        where_clauses.append('p.category = ?')
        params.append(category)

    # 3. Price filter
    where_clauses.append('p.price BETWEEN ? AND ?')
    params.extend([min_price, max_price])

    where_sql = ' AND '.join(where_clauses)
    sql = f'''
        SELECT p.*, s.shop_name, s.address, s.latitude, s.longitude,
               s.phone, s.is_open, s.category as shop_category
        FROM products p
        JOIN shops s ON p.shop_id = s.id
        WHERE {where_sql}
        ORDER BY p.search_count DESC, p.price ASC
        LIMIT 100
    '''
    rows = db.execute(sql, params).fetchall()

    # ── Filter by distance ────────────────────────────────────────────
    for row in rows:
        dist = haversine(user_lat, user_lng, row['latitude'], row['longitude'])
        if dist <= distance:
            r = dict(row)
            r['distance_km'] = round(dist, 2)
            results.append(r)

    # Sort
    if sort_by == 'price_asc':
        results.sort(key=lambda x: x['price'])
    elif sort_by == 'price_desc':
        results.sort(key=lambda x: -x['price'])
    elif sort_by == 'distance':
        results.sort(key=lambda x: x['distance_km'])
    elif sort_by == 'stock':
        results.sort(key=lambda x: -x['quantity'])

    # ── Increment search_count for matched products ───────────────────
    if results and query:
        ids = tuple(r['id'] for r in results[:20])
        placeholders = ','.join('?' * len(ids))
        db.execute(
            f'UPDATE products SET search_count = search_count + 1 WHERE id IN ({placeholders})',
            ids
        )
        user_id = session.get('user_id')
        db.execute(
            'INSERT INTO search_history (customer_id, product_name) VALUES (?, ?)',
            (user_id, query)
        )
        db.commit()

    # ── Build map shops data ──────────────────────────────────────────
    seen_shops = {}
    for r in results:
        sid = r['shop_id']
        if sid not in seen_shops:
            seen_shops[sid] = {
                'id': sid,
                'name': r['shop_name'],
                'address': r['address'],
                'lat': r['latitude'],
                'lng': r['longitude'],
                'phone': r['phone'],
                'category': r['shop_category'],
                'products': []
            }
        seen_shops[sid]['products'].append({
            'name': r['product_name'],
            'price': r['price'],
            'qty': r['quantity']
        })
    shops_map = list(seen_shops.values())

    # ── Apriori recommendations ───────────────────────────────────────
    rec_target = query or (category if category else (results[0]['product_name'] if results else ''))
    if rec_target:
        try:
            from models.apriori import get_recommendations
            recommendations = get_recommendations(rec_target, n=4)
        except Exception:
            recommendations = []

    db.close()

    return render_template('search.html',
                           query=query,
                           results=results,
                           shops_map=shops_map,
                           recommendations=recommendations,
                           categories=Config.CATEGORIES,
                           category_filter=category,
                           min_price=min_price,
                           max_price=max_price if max_price < 100000 else '',
                           distance=distance,
                           sort_by=sort_by,
                           user_lat=user_lat,
                           user_lng=user_lng,
                           default_lat=Config.DEFAULT_LAT,
                           default_lng=Config.DEFAULT_LNG)


# ──────────────────────────────────────────────────────────────────────────────
# Product Detail
# ──────────────────────────────────────────────────────────────────────────────

@search_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    db = get_db()
    prod = db.execute(
        '''SELECT p.*, s.shop_name, s.address, s.latitude, s.longitude,
                  s.phone, s.is_open, s.category as shop_category
           FROM products p JOIN shops s ON p.shop_id = s.id
           WHERE p.id = ?''',
        (product_id,)
    ).fetchone()

    if not prod:
        db.close()
        return render_template('404.html'), 404

    prod = dict(prod)

    # Same product from other shops
    other_shops = db.execute(
        '''SELECT p.*, s.shop_name, s.address, s.latitude, s.longitude, s.is_open
           FROM products p JOIN shops s ON p.shop_id = s.id
           WHERE LOWER(p.product_name) LIKE ? AND p.id != ? AND p.quantity > 0
           ORDER BY p.price ASC''',
        (f'%{prod["product_name"].lower()[:15]}%', product_id)
    ).fetchall()

    # Price history
    price_hist = db.execute(
        '''SELECT price, date FROM price_history WHERE product_id = ?
           ORDER BY date DESC LIMIT 30''',
        (product_id,)
    ).fetchall()

    # Increment search count
    db.execute(
        'UPDATE products SET search_count = search_count + 1 WHERE id = ?',
        (product_id,)
    )
    db.commit()

    # Price anomaly detection
    price_alert = {}
    try:
        from models.isolation_forest import analyze_shop_prices
        price_alert = analyze_shop_prices(db, prod['product_name'],
                                          prod['shop_id'], prod['price'])
    except Exception:
        price_alert = {'is_anomaly': False, 'message': ''}

    db.close()

    # Recommendations
    recommendations = []
    try:
        from models.apriori import get_recommendations
        recommendations = get_recommendations(prod['product_name'], n=4)
    except Exception:
        pass

    # Price history chart data
    ph_dates  = [row['date'] for row in reversed(price_hist)]
    ph_prices = [row['price'] for row in reversed(price_hist)]

    return render_template('product_detail.html',
                           product=prod,
                           other_shops=[dict(s) for s in other_shops],
                           recommendations=recommendations,
                           price_alert=price_alert,
                           price_history_dates=ph_dates,
                           price_history_prices=ph_prices,
                           categories=Config.CATEGORIES,
                           default_lat=Config.DEFAULT_LAT,
                           default_lng=Config.DEFAULT_LNG)


# ──────────────────────────────────────────────────────────────────────────────
# Autocomplete API
# ──────────────────────────────────────────────────────────────────────────────

@search_bp.route('/api/autocomplete')
def autocomplete():
    q = request.args.get('q', '').strip().lower()
    if len(q) < 2:
        return jsonify([])

    db = get_db()
    rows = db.execute(
        '''SELECT DISTINCT product_name FROM products
           WHERE LOWER(product_name) LIKE ?
           ORDER BY search_count DESC LIMIT 10''',
        (f'%{q}%',)
    ).fetchall()
    db.close()

    suggestions = [row['product_name'] for row in rows]

    # Add Word2Vec suggestions
    try:
        from models.word2vec import get_similar_terms
        extra = get_similar_terms(q, topn=5)
        # Capitalize each term nicely
        suggestions += [t.replace('_', ' ').title() for t in extra if t not in q]
    except Exception:
        pass

    return jsonify(list(dict.fromkeys(suggestions))[:10])
