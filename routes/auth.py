"""
NearShop — Authentication Routes
Handles customer and shop-owner registration, login, and logout.
"""
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, g)
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db
from config import Config

auth_bp = Blueprint('auth', __name__)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def owner_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'owner':
            flash('Access denied. Shop owner account required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


# ──────────────────────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session.get('role') == 'owner':
            return redirect(url_for('dashboard.dashboard'))
        return redirect(url_for('search.search'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role     = request.form.get('role', 'customer')

        db   = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE email = ? AND role = ?', (email, role)
        ).fetchone()
        db.close()

        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            session['name']    = user['name']
            session['email']   = user['email']
            session['role']    = user['role']
            flash(f'Welcome back, {user["name"]}!', 'success')
            if role == 'owner':
                return redirect(url_for('dashboard.dashboard'))
            return redirect(url_for('search.search'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html', categories=Config.CATEGORIES)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        role = request.form.get('role', 'customer')

        if role == 'customer':
            name     = request.form.get('name', '').strip()
            email    = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')

            if not all([name, email, password]):
                flash('All fields are required.', 'danger')
                return render_template('register.html', categories=Config.CATEGORIES)
            if len(password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
                return render_template('register.html', categories=Config.CATEGORIES)

            db = get_db()
            existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
            if existing:
                db.close()
                flash('Email already registered.', 'danger')
                return render_template('register.html', categories=Config.CATEGORIES)

            db.execute(
                'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
                (name, email, generate_password_hash(password), 'customer')
            )
            db.commit()
            user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            db.close()

            session['user_id'] = user['id']
            session['name']    = user['name']
            session['email']   = user['email']
            session['role']    = 'customer'
            flash('Account created successfully! Start searching.', 'success')
            return redirect(url_for('search.search'))

        elif role == 'owner':
            shop_name = request.form.get('shop_name', '').strip()
            owner_name = request.form.get('owner_name', '').strip()
            email      = request.form.get('email', '').strip().lower()
            phone      = request.form.get('phone', '').strip()
            address    = request.form.get('address', '').strip()
            category   = request.form.get('category', '')
            lat        = request.form.get('latitude', '15.1394')
            lng        = request.form.get('longitude', '76.9214')
            password   = request.form.get('password', '')

            if not all([shop_name, owner_name, email, phone, address, category, password]):
                flash('All fields are required.', 'danger')
                return render_template('register.html', categories=Config.CATEGORIES)
            if len(password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
                return render_template('register.html', categories=Config.CATEGORIES)

            try:
                lat = float(lat)
                lng = float(lng)
            except ValueError:
                lat = 15.1394
                lng = 76.9214

            db = get_db()
            existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
            if existing:
                db.close()
                flash('Email already registered.', 'danger')
                return render_template('register.html', categories=Config.CATEGORIES)

            db.execute(
                'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
                (owner_name, email, generate_password_hash(password), 'owner')
            )
            db.commit()
            user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

            db.execute(
                '''INSERT INTO shops (owner_id, shop_name, category, address, latitude, longitude, phone)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (user['id'], shop_name, category, address, lat, lng, phone)
            )
            db.commit()
            db.close()

            session['user_id'] = user['id']
            session['name']    = user['name']
            session['email']   = user['email']
            session['role']    = 'owner'
            flash(f'Shop "{shop_name}" registered successfully!', 'success')
            return redirect(url_for('dashboard.dashboard'))

    active_tab = request.args.get('tab', 'customer')
    return render_template('register.html', categories=Config.CATEGORIES, active_tab=active_tab)


@auth_bp.route('/logout')
def logout():
    name = session.get('name', 'User')
    session.clear()
    flash(f'Goodbye, {name}!', 'info')
    return redirect(url_for('main.index'))
