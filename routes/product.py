"""
NearShop — Product Routes
CRUD operations for shop owner product management.
"""
import os
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, jsonify, g)
from werkzeug.utils import secure_filename
from database.db import get_db
from config import Config
from routes.auth import owner_required
import datetime

product_bp = Blueprint('product', __name__)

ALLOWED = Config.ALLOWED_EXTENSIONS


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED


def save_image(file):
    """Save uploaded image and return filename."""
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Prefix with timestamp to avoid collisions
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = ts + filename
        upload_dir = Config.UPLOAD_FOLDER
        os.makedirs(upload_dir, exist_ok=True)
        file.save(os.path.join(upload_dir, filename))
        return filename
    return 'default.png'


# ──────────────────────────────────────────────────────────────────────────────
# Web Views
# ──────────────────────────────────────────────────────────────────────────────

@product_bp.route('/products')
@owner_required
def products():
    db = get_db()
    shop = db.execute(
        'SELECT * FROM shops WHERE owner_id = ?', (session['user_id'],)
    ).fetchone()

    if not shop:
        db.close()
        flash('Please set up your shop first.', 'warning')
        return redirect(url_for('dashboard.dashboard'))

    prods = db.execute(
        '''SELECT * FROM products WHERE shop_id = ? ORDER BY created_at DESC''',
        (shop['id'],)
    ).fetchall()
    db.close()

    return render_template('products.html',
                           products=prods,
                           shop=shop,
                           categories=Config.CATEGORIES)


# ──────────────────────────────────────────────────────────────────────────────
# API Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@product_bp.route('/api/products', methods=['GET'])
@owner_required
def api_list_products():
    db = get_db()
    shop = db.execute(
        'SELECT * FROM shops WHERE owner_id = ?', (session['user_id'],)
    ).fetchone()
    if not shop:
        db.close()
        return jsonify({'error': 'No shop found'}), 404

    prods = db.execute(
        'SELECT * FROM products WHERE shop_id = ? ORDER BY product_name',
        (shop['id'],)
    ).fetchall()
    db.close()
    return jsonify([dict(p) for p in prods])


@product_bp.route('/api/products', methods=['POST'])
@owner_required
def api_add_product():
    db = get_db()
    shop = db.execute(
        'SELECT * FROM shops WHERE owner_id = ?', (session['user_id'],)
    ).fetchone()
    if not shop:
        db.close()
        return jsonify({'error': 'No shop found'}), 404

    product_name = request.form.get('product_name', '').strip()
    category     = request.form.get('category', '').strip()
    description  = request.form.get('description', '').strip()
    price        = request.form.get('price', '0')
    quantity     = request.form.get('quantity', '0')
    brand        = request.form.get('brand', '').strip()
    image_file   = request.files.get('image')

    if not product_name or not category:
        db.close()
        flash('Product name and category are required.', 'danger')
        return redirect(url_for('product.products'))

    try:
        price    = float(price)
        quantity = int(quantity)
    except ValueError:
        db.close()
        flash('Invalid price or quantity.', 'danger')
        return redirect(url_for('product.products'))

    image_filename = save_image(image_file)

    db.execute(
        '''INSERT INTO products
           (shop_id, product_name, category, description, price, quantity, image, brand)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (shop['id'], product_name, category, description,
         price, quantity, image_filename, brand)
    )
    # Record initial price history
    prod_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.execute(
        'INSERT INTO price_history (product_id, price) VALUES (?, ?)',
        (prod_id, price)
    )
    db.commit()
    db.close()

    flash(f'Product "{product_name}" added successfully!', 'success')
    return redirect(url_for('product.products'))


@product_bp.route('/api/products/<int:product_id>', methods=['POST'])
@owner_required
def api_update_product(product_id):
    """Handles both full update (form) and quick stock update (JSON)."""
    db = get_db()
    shop = db.execute(
        'SELECT * FROM shops WHERE owner_id = ?', (session['user_id'],)
    ).fetchone()
    prod = db.execute(
        'SELECT * FROM products WHERE id = ? AND shop_id = ?',
        (product_id, shop['id'])
    ).fetchone() if shop else None

    if not prod:
        db.close()
        if request.is_json:
            return jsonify({'error': 'Product not found'}), 404
        flash('Product not found.', 'danger')
        return redirect(url_for('product.products'))

    # Quick stock update via JSON
    if request.is_json:
        data     = request.get_json()
        quantity = data.get('quantity')
        if quantity is None:
            db.close()
            return jsonify({'error': 'quantity required'}), 400
        db.execute(
            'UPDATE products SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (int(quantity), product_id)
        )
        db.commit()
        db.close()
        return jsonify({'success': True, 'quantity': quantity})

    # Full product update via form
    product_name = request.form.get('product_name', prod['product_name']).strip()
    category     = request.form.get('category', prod['category'])
    description  = request.form.get('description', prod['description'])
    price        = float(request.form.get('price', prod['price']))
    quantity     = int(request.form.get('quantity', prod['quantity']))
    brand        = request.form.get('brand', prod['brand'])
    image_file   = request.files.get('image')

    image_filename = prod['image']
    if image_file and image_file.filename:
        image_filename = save_image(image_file)

    db.execute(
        '''UPDATE products SET product_name=?, category=?, description=?,
           price=?, quantity=?, image=?, brand=?, updated_at=CURRENT_TIMESTAMP
           WHERE id=?''',
        (product_name, category, description, price, quantity,
         image_filename, brand, product_id)
    )

    # Track price change
    if price != prod['price']:
        db.execute(
            'INSERT INTO price_history (product_id, price) VALUES (?, ?)',
            (product_id, price)
        )

    db.commit()
    db.close()
    flash(f'Product "{product_name}" updated.', 'success')
    return redirect(url_for('product.products'))


@product_bp.route('/api/products/<int:product_id>/delete', methods=['POST'])
@owner_required
def api_delete_product(product_id):
    db = get_db()
    shop = db.execute(
        'SELECT * FROM shops WHERE owner_id = ?', (session['user_id'],)
    ).fetchone()
    if shop:
        prod = db.execute(
            'SELECT product_name FROM products WHERE id = ? AND shop_id = ?',
            (product_id, shop['id'])
        ).fetchone()
        if prod:
            db.execute('DELETE FROM products WHERE id = ?', (product_id,))
            db.execute('DELETE FROM price_history WHERE product_id = ?', (product_id,))
            db.commit()
            flash(f'Product "{prod["product_name"]}" deleted.', 'info')
    db.close()
    return redirect(url_for('product.products'))


# ──────────────────────────────────────────────────────────────────────────────
# Catalog — browse master product list and bulk-add to shop
# ──────────────────────────────────────────────────────────────────────────────

@product_bp.route('/catalog')
@owner_required
def catalog():
    """Catalog browser page."""
    db = get_db()
    shop = db.execute(
        'SELECT * FROM shops WHERE owner_id = ?', (session['user_id'],)
    ).fetchone()
    if not shop:
        db.close()
        flash('Please set up your shop first.', 'warning')
        return redirect(url_for('dashboard.dashboard'))

    # Get names of products already in this shop so we can mark them
    existing = db.execute(
        'SELECT LOWER(product_name) FROM products WHERE shop_id = ?',
        (shop['id'],)
    ).fetchall()
    existing_names = {row[0] for row in existing}
    db.close()

    return render_template('catalog.html',
                           shop=shop,
                           categories=Config.CATEGORIES,
                           existing_names=list(existing_names))


@product_bp.route('/api/catalog')
@owner_required
def api_catalog():
    """Return master product catalog grouped by category."""
    db = get_db()
    # Get one representative row per unique product name (lowest price across all shops)
    rows = db.execute('''
        SELECT product_name, category, brand, description,
               MIN(price) as price
        FROM products
        GROUP BY LOWER(product_name), category
        ORDER BY category, product_name
    ''').fetchall()
    db.close()

    catalog = {}
    for r in rows:
        cat = r['category']
        if cat not in catalog:
            catalog[cat] = []
        catalog[cat].append({
            'name':        r['product_name'],
            'category':    cat,
            'brand':       r['brand'] or '',
            'description': r['description'] or '',
            'suggested_price': round(float(r['price']), 2),
        })
    return jsonify(catalog)


@product_bp.route('/api/products/bulk', methods=['POST'])
@owner_required
def api_bulk_add():
    """Bulk-add selected catalog items to the owner's shop."""
    db = get_db()
    shop = db.execute(
        'SELECT * FROM shops WHERE owner_id = ?', (session['user_id'],)
    ).fetchone()
    if not shop:
        db.close()
        return jsonify({'error': 'No shop found'}), 404

    data  = request.get_json()
    items = data.get('items', [])   # [{name, category, brand, description, price, quantity}]

    if not items:
        db.close()
        return jsonify({'error': 'No items provided'}), 400

    added = 0
    skipped = 0
    for item in items:
        name     = item.get('name', '').strip()
        category = item.get('category', '').strip()
        price    = float(item.get('price', 0))
        quantity = int(item.get('quantity', 1))
        brand    = item.get('brand', '')
        desc     = item.get('description', '')

        if not name or price <= 0 or quantity <= 0:
            skipped += 1
            continue

        # Skip if already exists in this shop
        exists = db.execute(
            'SELECT id FROM products WHERE shop_id=? AND LOWER(product_name)=LOWER(?)',
            (shop['id'], name)
        ).fetchone()
        if exists:
            # Just update quantity + price instead
            db.execute(
                'UPDATE products SET quantity=?, price=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
                (quantity, price, exists['id'])
            )
            skipped += 1
            continue

        db.execute(
            '''INSERT INTO products
               (shop_id, product_name, category, description, price, quantity, image, brand)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (shop['id'], name, category, desc, price, quantity, 'default.png', brand)
        )
        prod_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        db.execute('INSERT INTO price_history (product_id, price) VALUES (?, ?)', (prod_id, price))
        added += 1

    db.commit()
    db.close()
    return jsonify({'success': True, 'added': added, 'skipped': skipped})
