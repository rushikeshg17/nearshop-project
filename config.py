import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'nearshop-secret-key-2024-ballari')
    DATABASE = os.path.join(BASE_DIR, 'database.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images', 'products')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # App info
    APP_NAME = 'NearShop'
    APP_TAGLINE = 'Find Products Near You Instantly'
    CITY = 'Ballari'
    STATE = 'Karnataka'

    # Map defaults (Ballari, KA)
    DEFAULT_LAT = 15.1394
    DEFAULT_LNG = 76.9214
    DEFAULT_ZOOM = 14
    DEFAULT_RADIUS_KM = 5

    # ML model paths
    MODELS_DIR = os.path.join(BASE_DIR, 'models')

    # Categories
    CATEGORIES = [
        'Vehicle Spare Parts',
        'Electrical',
        'Hardware',
        'Plumbing',
        'Footwear',
        'Stationery',
        'Books',
        'General Store',
    ]

    CATEGORY_ICONS = {
        'Vehicle Spare Parts': 'bi-gear-wide-connected',
        'Electrical':          'bi-lightning-charge-fill',
        'Hardware':            'bi-tools',
        'Plumbing':            'bi-droplet-fill',
        'Footwear':            'bi-bag-fill',
        'Stationery':          'bi-pencil-fill',
        'Books':               'bi-book-fill',
        'General Store':       'bi-shop-window',
    }

    CATEGORY_COLORS = {
        'Vehicle Spare Parts': '#3b82f6',
        'Electrical':          '#f59e0b',
        'Hardware':            '#6b7280',
        'Plumbing':            '#06b6d4',
        'Footwear':            '#8b5cf6',
        'Stationery':          '#10b981',
        'Books':               '#ef4444',
        'General Store':       '#f97316',
    }
